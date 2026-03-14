# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Configuration file writer tool with validation-before-write."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple

from google.adk.tools.tool_context import ToolContext
import jsonschema
import yaml

from ..utils import load_agent_config_schema
from ..utils.path_normalizer import sanitize_generated_file_path
from ..utils.resolve_root_directory import resolve_file_path
from .write_files import write_files

INVALID_FILENAME_CHARACTERS = frozenset('<>:"/\\|?*')
PARSED_CONFIG_KEY = "_parsed_config"
WORKFLOW_AGENT_CLASSES = frozenset({
    "SequentialAgent",
    "ParallelAgent",
    "LoopAgent",
})
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
CALLBACK_FIELD_NAMES = (
    "before_agent_callbacks",
    "after_agent_callbacks",
    "before_model_callbacks",
    "after_model_callbacks",
    "before_tool_callbacks",
    "after_tool_callbacks",
)


async def write_config_files(
    configs: Dict[str, str],
    tool_context: ToolContext,
    backup_existing: bool = False,  # Changed default to False - user should decide
    create_directories: bool = True,
) -> Dict[str, Any]:
  """Write multiple YAML configurations with comprehensive validation-before-write.

  This tool validates YAML syntax and AgentConfig schema compliance before
  writing files to prevent invalid configurations from being saved. It
  provides detailed error reporting and optional backup functionality.

  Args:
    configs: Dict mapping file_path to config_content (YAML as string)
    backup_existing: Whether to create timestamped backup of existing files
      before overwriting (default: False, User should decide)
    create_directories: Whether to create parent directories if they don't exist
      (default: True)

  Returns:
    Dict containing write operation results:
      Always included:
        - success: bool indicating if all write operations succeeded
        - total_files: number of files requested
        - successful_writes: number of files written successfully
        - files: dict mapping file_path to file results

      Success cases only (success=True):
        - file_size: size of written file in bytes
        - agent_name: extracted agent name from configuration
        - agent_class: agent class type (e.g., "LlmAgent")
        - warnings: list of warning messages for best practice violations.
                   Empty list if no warnings. Common warning types:
                   • Agent name formatting issues (special characters)
                   • Empty instruction for LlmAgent
                   • Missing sub-agent files
                   • Incorrect file extensions (.yaml/.yml)
                   • Mixed tool format consistency
        - target_file_path: normalized path used for writing the config
        - rename_applied: whether the file name was changed to match agent name
        - written_file_path: absolute path that was ultimately written

      Conditionally included:
        - backup: dict with backup information (if backup was created).
                 Contains:
                 • "backup_created": True (always True when present)
                 • "backup_path": absolute path to the timestamped backup file
                                 (format: "original.yaml.backup.{timestamp}")

      Error cases only (success=False):
        - error: descriptive error message explaining the failure
        - error_type: categorized error type for programmatic handling
        - validation_step: stage where validation process stopped.
                          Possible values:
                          • "yaml_parsing": YAML syntax is invalid
                          • "yaml_structure": YAML is valid but not a
                          dict/object
                          • "schema_validation": YAML violates AgentConfig
                          schema
                          • Not present: Error during file operations
        - validation_errors: detailed validation error list (for schema errors
        only)
        - retry_suggestion: helpful suggestions for fixing the error

  Examples:
    Write new configuration:
      result = await write_config_files({"my_agent.yaml": yaml_content})

    Write without backup:
      result = await write_config_files(
          {"temp_agent.yaml": yaml_content},
          backup_existing=False
      )

    Check backup information:
      result = await write_config_files({"existing_agent.yaml": new_content})
      if result["success"] and
      result["files"]["existing_agent.yaml"]["backup_created"]:
          backup_path = result["files"]["existing_agent.yaml"]["backup_path"]
          print(f"Original file backed up to: {backup_path}")

    Check validation warnings:
      result = await write_config_files({"agent.yaml": yaml_content})
      if result["success"] and result["files"]["agent.yaml"]["warnings"]:
          for warning in result["files"]["agent.yaml"]["warnings"]:
              print(f"Warning: {warning}")

    Handle validation errors:
      result = await write_config_files({"agent.yaml": invalid_yaml})
      if not result["success"]:
          step = result.get("validation_step", "file_operation")
          if step == "yaml_parsing":
              print("YAML syntax error:", result["error"])
          elif step == "schema_validation":
              print("Schema validation failed:", result["retry_suggestion"])
          else:
              print("Error:", result["error"])
  """
  result: Dict[str, Any] = {
      "success": True,
      "total_files": len(configs),
      "successful_writes": 0,
      "files": {},
      "errors": [],
  }

  validated_config_dicts: Dict[str, Dict[str, Any]] = {}
  normalized_path_to_original: Dict[str, str] = {}
  canonical_path_to_original: Dict[str, str] = {}
  rename_map: Dict[str, str] = {}

  session_state = None
  session = getattr(tool_context, "session", None)
  if session is not None:
    session_state = getattr(session, "state", None)
  project_folder_name: Optional[str] = None
  if session_state is not None:
    try:
      project_root = resolve_file_path(".", session_state)
      project_folder_name = project_root.name or None
    except Exception:
      project_folder_name = None

  # Step 1: Validate all configs before writing any files
  for file_path, config_content in configs.items():
    normalized_input_path = sanitize_generated_file_path(file_path)
    file_result = _validate_single_config(
        normalized_input_path, config_content, project_folder_name
    )
    result["files"][file_path] = file_result

    if file_result.get("success", False):
      parsed_config = file_result.pop(PARSED_CONFIG_KEY, None)
      if parsed_config is None:
        file_result["success"] = False
        file_result["error_type"] = "INTERNAL_VALIDATION_ERROR"
        file_result["error"] = "Failed to parse configuration content."
        result["success"] = False
        continue

      agent_name = file_result.get("agent_name")
      (
          target_path,
          rename_applied,
          sanitized_name,
          rename_warning,
      ) = _determine_target_file_path(normalized_input_path, agent_name)

      file_result["target_file_path"] = target_path
      file_result["rename_applied"] = rename_applied
      if rename_warning:
        warnings = file_result.get("warnings", [])
        warnings.append(rename_warning)
        file_result["warnings"] = warnings

      if rename_applied and sanitized_name and sanitized_name != agent_name:
        warnings = file_result.get("warnings", [])
        warnings.append(
            "Agent name normalized for filesystem compatibility:"
            f" '{agent_name}' -> '{sanitized_name}'"
        )
        file_result["warnings"] = warnings

      normalized_key = target_path
      if normalized_key in normalized_path_to_original:
        conflict_source = normalized_path_to_original[normalized_key]
        file_result["success"] = False
        file_result["error_type"] = "FILE_PATH_CONFLICT"
        file_result["error"] = (
            "Multiple agent configs target the same file path after"
            f" normalization: '{conflict_source}' and '{file_path}'"
        )
        result["success"] = False
        continue
      normalized_path_to_original[normalized_key] = file_path

      canonical_key = _canonical_path_key(normalized_key, session_state)
      if canonical_key in canonical_path_to_original:
        conflict_source = canonical_path_to_original[canonical_key]
        file_result["success"] = False
        file_result["error_type"] = "FILE_PATH_CONFLICT"
        file_result["error"] = (
            "Multiple agent configs resolve to the same file path after"
            f" normalization: '{conflict_source}' and '{file_path}'"
        )
        result["success"] = False
        continue
      canonical_path_to_original[canonical_key] = file_path

      if normalized_key != file_path:
        rename_map[file_path] = normalized_key

      validated_config_dicts[normalized_key] = parsed_config
    else:
      result["success"] = False

  if result["success"] and validated_config_dicts:
    if rename_map:
      reference_map = _build_reference_map(rename_map)
      for config_dict in validated_config_dicts.values():
        _update_sub_agent_references(config_dict, reference_map)

    validated_configs: Dict[str, str] = {}
    for normalized_path, config_dict in validated_config_dicts.items():
      validated_configs[normalized_path] = yaml.safe_dump(
          config_dict,
          sort_keys=False,
      )

    write_result: Dict[str, Any] = await write_files(
        validated_configs,
        tool_context,
        create_backup=backup_existing,
        create_directories=create_directories,
    )

    # Merge write results with validation results
    files_data = write_result.get("files", {})
    for written_path, write_info in files_data.items():
      canonical_written_key = _canonical_path_key(written_path, session_state)
      original_key = canonical_path_to_original.get(canonical_written_key)

      if original_key and original_key in result["files"]:
        file_entry = result["files"][original_key]
        if isinstance(file_entry, dict):
          file_entry.update({
              "file_size": write_info.get("file_size", 0),
              "backup_created": write_info.get("backup_created", False),
              "backup_path": write_info.get("backup_path"),
              "written_file_path": written_path,
          })
          if write_info.get("error"):
            file_entry["success"] = False
            file_entry["error"] = write_info["error"]
            result["success"] = False
          else:
            result["successful_writes"] = result["successful_writes"] + 1

  return result


def _build_reference_map(rename_map: Dict[str, str]) -> Dict[str, str]:
  """Build lookup for updating sub-agent config paths after renames."""
  reference_map: Dict[str, str] = {}
  for original, target in rename_map.items():
    original_path = Path(original)
    target_path = Path(target)

    candidates = {
        original: target,
        str(original_path): str(target_path),
        original_path.as_posix(): target_path.as_posix(),
        original_path.name: target_path.name,
    }

    # Ensure Windows-style separators are covered when running on POSIX.
    candidates.setdefault(
        str(original_path).replace("\\", "/"),
        str(target_path).replace("\\", "/"),
    )

    for candidate, replacement in candidates.items():
      reference_map[candidate] = replacement

  return reference_map


def _update_sub_agent_references(
    config_dict: Dict[str, Any], reference_map: Dict[str, str]
) -> None:
  """Update sub-agent config_path entries based on rename map."""
  if not reference_map:
    return

  sub_agents = config_dict.get("sub_agents")
  if not isinstance(sub_agents, list):
    return

  for sub_agent in sub_agents:
    if not isinstance(sub_agent, dict):
      continue

    config_path = sub_agent.get("config_path")
    if not isinstance(config_path, str):
      continue

    new_path = reference_map.get(config_path)
    if new_path is None:
      try:
        normalized = str(Path(config_path))
        new_path = reference_map.get(normalized)
      except (OSError, ValueError):
        normalized = None

    if new_path is None and normalized is not None:
      new_path = reference_map.get(Path(normalized).as_posix())

    if new_path is None:
      try:
        base_name = Path(config_path).name
        new_path = reference_map.get(base_name)
      except (OSError, ValueError):
        new_path = None

    if new_path:
      sub_agent["config_path"] = new_path


def _canonical_path_key(
    path: str, session_state: Optional[Dict[str, Any]]
) -> str:
  """Create a canonical absolute path string for consistent lookups."""
  try:
    resolved_path = resolve_file_path(path, session_state)
  except (OSError, ValueError, RuntimeError):
    resolved_path = Path(path)

  try:
    return str(resolved_path.resolve())
  except (OSError, RuntimeError):
    return str(resolved_path)


def _validate_single_config(
    file_path: str,
    config_content: str,
    project_folder_name: Optional[str] = None,
) -> Dict[str, Any]:
  """Validate a single configuration file.

  Returns validation results for one config file.
  """
  try:
    # Convert to absolute path
    path = Path(file_path).resolve()

    # Step 1: Parse YAML content
    try:
      config_dict = yaml.safe_load(config_content)
    except yaml.YAMLError as e:
      return {
          "success": False,
          "error_type": "YAML_PARSE_ERROR",
          "error": f"Invalid YAML syntax: {str(e)}",
          "file_path": str(path),
          "validation_step": "yaml_parsing",
      }

    if not isinstance(config_dict, dict):
      return {
          "success": False,
          "error_type": "YAML_STRUCTURE_ERROR",
          "error": "YAML content must be a dictionary/object",
          "file_path": str(path),
          "validation_step": "yaml_structure",
      }

    # Step 2: Validate against AgentConfig schema
    validation_result = _validate_against_schema(config_dict)
    if not validation_result["valid"]:
      return {
          "success": False,
          "error_type": "SCHEMA_VALIDATION_ERROR",
          "error": "Configuration does not comply with AgentConfig schema",
          "validation_errors": validation_result["errors"],
          "file_path": str(path),
          "validation_step": "schema_validation",
          "retry_suggestion": _generate_retry_suggestion(
              validation_result["errors"]
          ),
      }

    # Step 3: Additional structural validation
    # TODO: b/455645705 - Remove once the frontend performs these validations before calling
    # this tool.
    name_warning = _normalize_agent_name_field(config_dict, path)
    structural_validation = _validate_structure(config_dict, path)
    warnings = list(structural_validation.get("warnings", []))
    warnings.extend(_strip_workflow_agent_fields(config_dict))
    if name_warning:
      warnings.append(name_warning)
    name_validation_error = _require_valid_agent_name(config_dict, path)
    if name_validation_error is not None:
      return name_validation_error
    model_validation_error = _require_llm_agent_model(config_dict, path)
    if model_validation_error is not None:
      return model_validation_error
    project_scope_result = _enforce_project_scoped_references(
        config_dict, project_folder_name, path
    )
    warnings.extend(project_scope_result.get("warnings", []))
    project_scope_error = project_scope_result.get("error")
    if project_scope_error is not None:
      return project_scope_error

    # Success response with validation metadata
    return {
        "success": True,
        "file_path": str(path),
        "agent_name": config_dict.get("name", "unknown"),
        "agent_class": config_dict.get("agent_class", "LlmAgent"),
        "warnings": warnings,
        PARSED_CONFIG_KEY: config_dict,
    }

  except Exception as e:
    return {
        "success": False,
        "error_type": "UNEXPECTED_ERROR",
        "error": f"Unexpected error during validation: {str(e)}",
        "file_path": file_path,
    }


def _validate_against_schema(
    config_dict: Dict[str, Any],
) -> Dict[str, Any]:
  """Validate configuration against AgentConfig.json schema."""
  try:
    schema = load_agent_config_schema(raw_format=False)
    jsonschema.validate(config_dict, schema)

    return {"valid": True, "errors": []}

  except jsonschema.ValidationError as e:
    # JSONSCHEMA QUIRK WORKAROUND: Handle false positive validation errors
    #
    # Problem: When AgentConfig schema uses anyOf with inheritance hierarchies,
    # jsonschema throws ValidationError even for valid configs that match multiple schemas.
    #
    # Example scenario:
    # - AgentConfig schema: {"anyOf": [{"$ref": "#/$defs/LlmAgentConfig"},
    #                                  {"$ref": "#/$defs/SequentialAgentConfig"},
    #                                  {"$ref": "#/$defs/BaseAgentConfig"}]}
    # - Input config: {"agent_class": "SequentialAgent", "name": "test", ...}
    # - Result: Config is valid against both SequentialAgentConfig AND BaseAgentConfig
    #   (due to inheritance), but jsonschema considers this an error.
    #
    # Error message format:
    # "{'agent_class': 'SequentialAgent', ...} is valid under each of
    #  {'$ref': '#/$defs/SequentialAgentConfig'}, {'$ref': '#/$defs/BaseAgentConfig'}"
    #
    # Solution: Detect this specific error pattern and treat as valid since the
    # config actually IS valid - it just matches multiple compatible schemas.
    if "is valid under each of" in str(e.message):