# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json
import random
import socket
import threading
import time
import uuid
from collections import defaultdict
from collections.abc import Mapping
from typing import Any, Dict, List, Literal, Optional, Tuple, cast

import numpy as np
import requests
import torch
from flask import Flask, Response, abort, request
from tensordict import TensorDict
from verl import DataProto

from agentlightning import LLM, AgentLightningServer, NamedResources, RolloutLegacy
from agentlightning.adapter.triplet import TraceToTripletBase
from agentlightning.llm_proxy import LLMProxy, ModelConfig
from agentlightning.reward import find_final_reward
from agentlightning.store.base import LightningStore
from agentlightning.types import EnqueueRolloutRequest, Rollout, RolloutConfig, Task
from contrib.agentlightning.contrib.adapter.triplet_group import TracerTraceToTripletGroup

__all__ = [
    "AgentModeDaemon",
    "get_left_padded_ids_and_attention_mask",
    "get_right_padded_ids_and_attention_mask",
]


def get_left_padded_ids_and_attention_mask(
    ids: List[int], max_length: int, pad_token_id: int
) -> Tuple[List[int], List[int]]:
    """
    Left-pad (or truncate) a sequence of token IDs to a fixed length,
    and build the corresponding attention mask.

    Args:
        ids:             the original list of token IDs.
        max_length:      desired total length after padding/truncation.
        pad_token_id:    ID to use for padding.

    Returns:
        padded_ids (any):      list of length == max_length.
        attention_mask (any):  list of same length: 1 for non-pad tokens, 0 for pads.
    """
    seq_len = len(ids)

    if seq_len >= max_length:
        # too long → truncate from the left, keep the last max_length tokens
        trimmed = ids[-max_length:]
        attention_mask = [1] * max_length
        return trimmed, attention_mask

    # too short → pad on the left
    pad_len = max_length - seq_len
    padded_ids = [pad_token_id] * pad_len + ids
    attention_mask = [0] * pad_len + [1] * seq_len
    return padded_ids, attention_mask


def get_right_padded_ids_and_attention_mask(
    ids: List[int], max_length: int, pad_token_id: int
) -> Tuple[List[int], List[int]]:
    """
    Right-pad (or truncate) a sequence of token IDs to a fixed length,
    and build the corresponding attention mask.

    Args:
        ids:            the original list of token IDs.
        max_length:     desired total length after padding/truncation.
        pad_token_id:   ID to use for padding.

    Returns:
        padded_ids (any):     list of length == max_length.
        attention_mask (any): list of same length: 1 for non-pad tokens, 0 for pads.
    """
    seq_len = len(ids)

    if seq_len >= max_length:
        # too long → truncate to the first max_length tokens
        trimmed = ids[:max_length]
        attention_mask = [1] * max_length
        return trimmed, attention_mask

    # too short → pad on the right
    pad_len = max_length - seq_len
    padded_ids = ids + [pad_token_id] * pad_len
    attention_mask = [1] * seq_len + [0] * pad_len
    return padded_ids, attention_mask


def _find_available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _to_native(obj: Any) -> Any:
    """Convert data retrieved from Parquet to data usable in AGL server."""
    # 1) Arrays -> list (then recurse)
    if isinstance(obj, np.ndarray):
        return _to_native(obj.tolist())

    # 2) NumPy scalar types -> Python scalars
    if isinstance(obj, np.generic):
        return _to_native(obj.item())

    # 3) Dict-like -> dict
    if isinstance(obj, Mapping):
        return {_to_native(k): _to_native(v) for k, v in obj.items()}  # type: ignore

    # 4) Lists/Tuples/Sets -> list
    if isinstance(obj, (list, tuple, set)):
        return [_to_native(x) for x in obj]  # type: ignore

    # 5) Anything else: leave as-is
    return obj


class EnvAgentModeDaemon:
    """
    AgentModeDaemon using the AgentLightningServer SDK.

    This class manages the server lifecycle, task queueing, and results
    retrieval, while also running a proxy server for LLM requests. It maintains
    the original interface for compatibility with the RayPPOTrainer.
    """

    def __init__(
        self,
        port: Optional[int],
        train_rollout_n: int,
        train_information: Dict[str, Any],
        tokenizer: Any,
        mini_batch_size: int,
        pad_token_id: int,
        reward_fillna_value: float = 0.0,
        llm_timeout_seconds: float = 1200.0,
        mode: Literal["v0", "v1"] = "v1",
        llm_proxy: LLMProxy | None = None,
        store: LightningStore | None = None,
        adapter: TraceToTripletBase | None = None,
    ):
        self.mode = mode
        self.llm_timeout_seconds = llm_timeout_seconds

        # Server and Task Configuration
        if mode == "v0":
            assert port is not None
            self.server_port = port
            self.server = AgentLightningServer(
                host="0.0.0.0", port=self.server_port, task_timeout_seconds=self.llm_timeout_seconds
            )
            self.proxy_port = _find_available_port()  # Run proxy on a different port
        else:
            assert store is not None
            self.store = store
            if llm_proxy is None:
                self.llm_proxy = LLMProxy(
                    port=_find_available_port(),
                    model_list=[],
                    store=store,
                )
            else:
                # Reuse the existing LLM proxy (probably configured by user)
                self.llm_proxy = llm_proxy

            # if adapter is None:
            #     self.adapter = TracerTraceToTripletGroup()
            # else:
            #     # Reuse the one from trainer
            #     self.adapter = adapter
            self.adapter = TracerTraceToTripletGroup()

            self._internal_loop: Optional[asyncio.AbstractEventLoop] = None
            self._internal_loop_thread = threading.Thread(target=self._internal_loop_runner, daemon=True)
            self._internal_loop_thread.start()

        # Training and Data Configuration
        self.train_rollout_n = train_rollout_n
        self.train_information = train_information
        self.mini_batch_size = mini_batch_size
        self.pad_token_id = pad_token_id
        self.tokenizer = tokenizer
        self.reward_fillna_value = reward_fillna_value

        # Internal State
        self.backend_llm_server_addresses: List[str] = []
        self._total_tasks_queued = 0
        self._completed_rollouts_v0: Dict[str, RolloutLegacy] = {}
        self._task_id_to_original_sample: Dict[str, Dict[str, Any]] = {}
        self._server_thread: Optional[threading.Thread] = None
        self._proxy_thread: Optional[threading.Thread] = None
        self.is_train = True

    def _internal_loop_runner(self):
        """Run the internal loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._internal_loop = loop
        loop.run_forever()
        loop.close()

    def _start_proxy_server_v0(self):
        """
        Initializes and runs a Flask-based proxy server in a separate thread.
        This proxy load-balances requests to the actual backend LLM servers.
        """
        app = Flask(__name__)

        num_requests = 0
        last_request_time = 0

        @app.route("/v1/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
        def proxy(path: str):  # type: ignore
            if not self.backend_llm_server_addresses:
                abort(503, description="No backend LLM servers available.")

            # Randomly choose a backend server for load balancing
            target_server = random.choice(self.backend_llm_server_addresses)
            target_url = f"http://{target_server}/v1/{path}"

            # Copy client request headers, removing the Host header
            headers = {key: value for key, value in request.headers if key.lower() != "host"}

            # Log the request for debugging
            nonlocal num_requests, last_request_time
            current_time = time.time()
            num_requests += 1
            if current_time - last_request_time > 60 or num_requests == 1 or num_requests % 100 == 0:
                print(f"Proxying {request.method} request to {target_server}. Request data: {request.get_data()}")
            last_request_time = current_time

            try:
                # Forward the request to the target backend
                resp = requests.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    params=request.args,  # type: ignore
                    data=request.get_data(),
                    cookies=request.cookies,
                    allow_redirects=False,
                    timeout=self.llm_timeout_seconds,
                )
                # Filter out hop-by-hop headers before returning the response
                excluded_headers = [
                    "content-encoding",
                    "content-length",
                    "transfer-encoding",
                    "connection",
                    "keep-alive",
                    "proxy-authenticate",
                    "proxy-authorization",
                    "te",
                    "trailers",
                    "upgrade",
                ]
                response_headers = [
                    (name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers
                ]
                if resp.status_code == 200:
                    # NOTE: from Zhiyuan's code.
                    # https://github.com/hzy46/verl_agent_mode/blob/2db65ea9858f645a914120357412a7540f8bd82d/verl/trainer/ppo/ray_trainer.py#L692-L711
                    # request_json = json.loads(request.get_data().decode("utf-8"))
                    response_json = json.loads(resp.content.decode("utf-8"))
                    # response_message = ChatCompletion(**response_json).choices[0].message.model_dump(exclude_unset=True, exclude_none=True)
                    # tool_schemas = request_json.get("tools", None)
                    # prompt_ids = self.tokenizer.apply_chat_template(request_json["messages"], tools=tool_schemas, add_generation_prompt=True, tokenize=True)
                    # full_ids = self.tokenizer.apply_chat_template(request_json["messages"] + [response_message], tools=tool_schemas, add_generation_prompt=False, tokenize=True)
                    # TBD: response_ids sometimes ends with "<eos_id>\n", shall we keep the extra "\n"?
                    # sometimes it has some differences with the hacky method in the end, but this should align with ToolCompletionCallback
                    # response_ids = full_ids[len(prompt_ids):]

                    # NOTE (yuge): They are different. Don't know why.
                    # assert response_json['prompt_token_ids'] == prompt_ids
                    # patched_response_ids = response_json['response_token_ids'][0]
                    # assert patched_response_ids == response_ids[:len(patched_response_ids)], f"{patched_response_ids} != {response_ids[:len(patched_response_ids)]}"
                    # response_json['prompt_token_ids'] = prompt_ids
                    # response_json['response_token_ids'] = [response_ids]
                    replaced_return_content = json.dumps(response_json).encode("utf-8")
                    return Response(replaced_return_content, status=resp.status_code, headers=response_headers)
                return Response(resp.content, resp.status_code, response_headers)
            except requests.exceptions.RequestException as e:
                abort(500, description=f"Error proxying request: {e}")

        def run_app():
            app.run(host="0.0.0.0", port=self.proxy_port, threaded=True, debug=False)

        self._proxy_thread = threading.Thread(target=run_app, daemon=True)
        self._proxy_thread.start()
        print(f"Proxy server running on port {self.proxy_port}")

    async def _update_proxy_server_v1(self):
        model_name = self.train_information.get("model")
        if not model_name:
            raise ValueError("Model name is not set.")
        self.llm_proxy.update_model_list(
            [
                ModelConfig(
                    {
                        "model_name": model_name,
                        "litellm_params": {
                            "model": "hosted_vllm/" + model_name,
                            "api_base": f"http://{address}/v1/",
                        },
                    }
                )
                for address in self.backend_llm_server_addresses
            ],
        )

        await self.llm_proxy.restart()

    def start(self):
        """Starts the main AgentLightningServer and the proxy server."""

        if self.mode == "v0":

            def run_server():
                """Run the AgentLightningServer in a separate thread."""
                asyncio.run(self.server.run_forever())

            self._server_thread = threading.Thread(target=run_server, daemon=True)
            self._server_thread.start()

            # Wait for the server's internal startup event to be set.
            print("Waiting for AgentLightningServer to start...")
            is_ready = self.server.startup_event.wait(timeout=20.0)  # Wait up to 20s
            if not is_ready:
                raise RuntimeError("AgentLightningServer failed to start within the timeout period.")

            print(f"AgentLightningServer control plane running on port {self.server_port}")

            self._start_proxy_server_v0()
        else:
            # Agent lightning server is no longer needed;
            # Start proxy server in _async_set_up
            pass

    async def _async_set_up(self, data: Dict[str, Any], server_addresses: List[str], is_train: bool = True):
        """Async helper to set up data and resources on the server."""
        self.clear_data_and_server()
        if server_addresses != self.backend_llm_server_addresses:
            self.backend_llm_server_addresses = server_addresses
            if self.mode == "v1" and not self.llm_proxy.is_running():
                await self._update_proxy_server_v1()
        self.is_train = is_train

        # 1. Update resources on the server for clients to use
        if self.mode == "v0":
            llm_resource = LLM(
                endpoint=f"http://127.0.0.1:{self.proxy_port}/v1",
                model=self.train_information.get("model", "default-model"),
                sampling_parameters={
                    "temperature": self.train_information.get("temperature", 0.7 if is_train else 0.0)
                },
            )
        else:
            llm_resource = self.llm_proxy.as_resource(
                sampling_parameters={
                    "temperature": self.train_information.get("temperature", 0.7 if is_train else 0.0)
                },
            )

        resources: NamedResources = {"main_llm": llm_resource}

        if self.mode == "v0":
            resources_id = await self.server.update_resources(resources)
        else:
            resources_update = await self.store.add_resources(resources)
            resources_id = resources_update.resources_id

        # 2. Queue tasks for agents to process
        keys = list(data.keys())
        num_samples = len(data[keys[0]])
        rollouts_per_sample = self.train_rollout_n if is_train else 1

        enqueue_rollout_requests: List[EnqueueRolloutRequest] = []
        data_id_to_original_sample: Dict[str, Dict[str, Any]] = {}

        for i in range(num_samples):
            data_id = str(uuid.uuid4())
            original_sample = {key: data[key][i] for key in keys}
            original_sample["data_id"] = data_id
            data_id_to_original_sample[data_id] = original_sample

            # For training, each sample is rolled out multiple times
            # Data ID is different from Rollout ID, as one data can have multiple rollouts.
            for _ in range(rollouts_per_sample):
                task_metadata = {"data_id": data_id, "is_train": is_train}
                if self.mode == "v0":
                    # Queue immediately
                    rollout_id = await self.server.queue_task(
                        sample=_to_native(original_sample),
                        mode="train" if is_train else "val",
                        resources_id=resources_id,
                        metadata=task_metadata,
                    )

                    # Store original sample data to reconstruct batch information later
                    self._task_id_to_original_sample[rollout_id] = original_sample
                    self._total_tasks_queued += 1
                else:
                    # Collect tasks to enqueue in batch and queue them later
                    enqueue_rollout_requests.append(
                        EnqueueRolloutRequest(
                            input=_to_native(original_sample),
                            mode="train" if is_train else "val",
                            resources_id=resources_id,
                            config=RolloutConfig(
                                unresponsive_seconds=self.llm_timeout_seconds,
                                timeout_seconds=self.llm_timeout_seconds,
                            ),
                            metadata=task_metadata,
                        )
                    )

        if self.mode == "v1":
            # Enqueue all the tasks in a single batch
            rollouts = await self.store.enqueue_many_rollouts(enqueue_rollout_requests)
            self._task_id_to_original_sample.update(
                {
                    # Recover the original data and store it for later use.
                    rollout.rollout_id: data_id_to_original_sample[cast(Dict[str, Any], rollout.metadata)["data_id"]]
                    for rollout in rollouts
                }
            )
            self._total_tasks_queued += len(rollouts)

    def set_up_data_and_server(self, data: Dict[str, Any], server_addresses: List[str], is_train: bool = True):
        """Synchronous wrapper for setting up data and server resources."""
        coro = self._async_set_up(data, server_addresses, is_train)

        if self.mode == "v0":
            if not self.server.loop or not self.server.startup_event.is_set():
                raise RuntimeError("Server is not running or ready.")

            future = asyncio.run_coroutine_threadsafe(coro, self.server.loop)

        else:
            if self._internal_loop is None:
                raise RuntimeError("Internal loop is not running.")
            future = asyncio.run_coroutine_threadsafe(coro, self._internal_loop)
        try:
            future.result(timeout=60)  # Wait for completion with a timeout
        except Exception as e:
            print(f"Failed to set up data on server: {e}")
            raise

    def _validate_data(self, rollout: RolloutLegacy):
        if rollout.final_reward is None:
            print(
                f"Warning: Reward is None for rollout {rollout.rollout_id}, will be auto-set to {self.reward_fillna_value}."
            )
        if rollout.triplets is None:
            print(f"Warning: Triplet is None for rollout {rollout.rollout_id}.")
        elif len(rollout.triplets) == 0:
            print(f"Warning: Length of triplets is 0 for rollout {rollout.rollout_id}.")
        elif any(not r.response.get("token_ids", []) for r in rollout.triplets):
            print(f"Warning: Rollout {rollout.rollout_id} contains empty response: {rollout.triplets}")
        elif any(not r.prompt.get("token_ids", []) for r in rollout.triplets):
            print(f"Warning: Rollout {rollout.rollout_id} contains empty prompt: {rollout.triplets}")

    async def _validate_data_v1(self, rollout: Rollout) -> RolloutLegacy:
        """Convert Rollout to RolloutLegacy and validate.

        1. Task: construct from Rollout
        2. Triplets: obtained by querying spans and feeding into the adapter
        3. Final reward: extracted from last triplet's reward, searching backwards if not found
        """
        # Query spans for this rollout (latest attempt)
        spans = await self.store.query_spans(rollout.rollout_id, attempt_id="latest")
        final_reward = find_final_reward(spans)

        # Convert spans to triplets using the adapter
        if not spans:
            # No triplets found, will emit a warning later.
            triplets = []
        else:
            # triplets = self.adapter.adapt(spans)
            triplets = self.adapter.adapt_group(spans)

        # # Extract final reward from triplets
        # final_reward: Optional[float] = None
        # if triplets:
        #     # Search backwards through triplets for the first non-None reward
        #     for triplet in reversed(triplets):
        #         if triplet.reward is not None:
        #             final_reward = triplet.reward
        #             break

        # Construct the Task object from Rollout
        task = Task(