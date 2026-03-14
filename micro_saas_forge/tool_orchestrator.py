"""
╔══════════════════════════════════════════════════════════════╗
║  Tool Orchestrator v1.0                                      ║
║  AsyncIO queue + per-tool circuit breaker + retry logic       ║
╚══════════════════════════════════════════════════════════════╝
"""
import asyncio
import time
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Any

from titan_config import (
    TOOL_QUEUE_MAX_SIZE,
    TOOL_EXECUTION_TIMEOUT,
    TOOL_RETRY_ATTEMPTS,
    TOOL_RETRY_DELAY,
    CB_FAILURE_THRESHOLD,
    CB_RECOVERY_TIMEOUT,
    CB_HALF_OPEN_MAX_CALLS,
)

log = logging.getLogger("titan_brain.orchestrator")


# ---------------------------------------------------------------------------
# Circuit Breaker
# ---------------------------------------------------------------------------
class CircuitState(Enum):
    CLOSED = "CLOSED"           # Normal operation
    OPEN = "OPEN"               # Failing, reject calls
    HALF_OPEN = "HALF_OPEN"     # Testing recovery


@dataclass
class CircuitBreaker:
    """Per-tool circuit breaker to prevent cascading failures."""
    name: str
    failure_threshold: int = CB_FAILURE_THRESHOLD
    recovery_timeout: float = CB_RECOVERY_TIMEOUT
    half_open_max: int = CB_HALF_OPEN_MAX_CALLS

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    half_open_calls: int = 0

    # Metrics
    total_calls: int = 0
    total_successes: int = 0
    total_failures: int = 0

    def can_execute(self) -> bool:
        """Check if a call is allowed through the circuit."""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                log.info(f"⚡ Circuit [{self.name}] transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max
        return False

    def record_success(self):
        """Record a successful call."""
        self.total_calls += 1
        self.total_successes += 1
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            log.info(f"✅ Circuit [{self.name}] recovered → CLOSED")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0  # Reset consecutive failures

    def record_failure(self):
        """Record a failed call."""
        self.total_calls += 1
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            log.warning(f"🔴 Circuit [{self.name}] recovery failed → OPEN")
            self.state = CircuitState.OPEN
        elif self.failure_count >= self.failure_threshold:
            log.warning(f"🔴 Circuit [{self.name}] opened after {self.failure_count} failures")
            self.state = CircuitState.OPEN

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "total_calls": self.total_calls,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "success_rate": f"{self.total_successes / max(self.total_calls, 1) * 100:.1f}%",
        }


# ---------------------------------------------------------------------------
# Tool Orchestrator
# ---------------------------------------------------------------------------
@dataclass
class ToolTask:
    tool_name: str
    args: dict
    future: asyncio.Future = field(default=None)


class ToolOrchestrator:
    """
    Manages tool execution with:
    - Async task queue (backpressure control)
    - Per-tool circuit breakers
    - Retry with delay
    - Execution timeout
    """

    def __init__(self, executor_fn: Callable = None):
        """
        Args:
            executor_fn: async callable(tool_name, args) -> str
        """
        self.executor_fn = executor_fn
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=TOOL_QUEUE_MAX_SIZE)
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self._worker_task = None
        self._running = False

    def _get_breaker(self, tool_name: str) -> CircuitBreaker:
        if tool_name not in self.circuit_breakers:
            self.circuit_breakers[tool_name] = CircuitBreaker(name=tool_name)
        return self.circuit_breakers[tool_name]

    async def start(self):
        """Start the background worker that processes the queue."""
        self._running = True
        self._worker_task = asyncio.create_task(self._worker_loop())
        log.info(f"🔧 ToolOrchestrator started (queue_max={TOOL_QUEUE_MAX_SIZE})")

    async def stop(self):
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()

    async def submit(self, tool_name: str, args: dict) -> str:
        """
        Submit a tool for execution. Returns the result string.
        Blocks if the queue is full (backpressure).
        """
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        task = ToolTask(tool_name=tool_name, args=args, future=future)

        try:
            self.queue.put_nowait(task)
        except asyncio.QueueFull:
            log.warning(f"⚠️ Tool queue full! Dropping task: {tool_name}")
            return f"⚠️ System overloaded. Tool '{tool_name}' dropped."

        return await future

    async def _worker_loop(self):
        """Background worker that pulls tasks from the queue."""
        while self._running:
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                result = await self._execute_with_retry(task.tool_name, task.args)
                if not task.future.done():
                    task.future.set_result(result)
            except asyncio.TimeoutError:
                continue  # No task, loop again
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"Worker error: {e}")

    async def _execute_with_retry(self, tool_name: str, args: dict) -> str:
        """Execute a tool with circuit breaker check and retry logic."""
        breaker = self._get_breaker(tool_name)

        if not breaker.can_execute():
            return f"🔴 Circuit OPEN for '{tool_name}'. Retry in {CB_RECOVERY_TIMEOUT}s."

        for attempt in range(TOOL_RETRY_ATTEMPTS + 1):
            try:
                if self.executor_fn is None:
                    return f"❌ No executor function registered for orchestrator."

                result = await asyncio.wait_for(
                    self.executor_fn(tool_name, args),
                    timeout=TOOL_EXECUTION_TIMEOUT,
                )
                breaker.record_success()
                return result

            except asyncio.TimeoutError:
                breaker.record_failure()
                log.warning(f"⏰ Tool '{tool_name}' timed out (attempt {attempt + 1})")
                if attempt < TOOL_RETRY_ATTEMPTS:
                    await asyncio.sleep(TOOL_RETRY_DELAY)
            except Exception as e:
                breaker.record_failure()
                log.error(f"💥 Tool '{tool_name}' failed (attempt {attempt + 1}): {e}")
                if attempt < TOOL_RETRY_ATTEMPTS:
                    await asyncio.sleep(TOOL_RETRY_DELAY)

        return f"❌ Tool '{tool_name}' failed after {TOOL_RETRY_ATTEMPTS + 1} attempts."

    def get_health(self) -> dict:
        """Return health status of all circuit breakers."""
        return {
            "queue_size": self.queue.qsize(),
            "queue_max": TOOL_QUEUE_MAX_SIZE,
            "tools": {
                name: breaker.get_status()
                for name, breaker in self.circuit_breakers.items()
            },
        }
