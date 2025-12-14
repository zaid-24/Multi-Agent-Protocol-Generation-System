from typing import Dict, Any, Callable
from datetime import datetime, timezone
import functools
import time
from uuid import uuid4

from ..state import FoundryState
from ..db import SessionLocal, AgentRun

StateUpdate = Dict[str, Any]
AgentFn = Callable[[FoundryState], StateUpdate]


def now_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


def _serialize_value(value: Any) -> Any:
    """
    Best-effort serialization of values for logging.

    - Pydantic models -> dict via model_dump()
    - Lists -> serialize elements recursively
    - Dicts -> serialize values recursively
    - Other types -> returned as-is
    """
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_serialize_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    return value


def log_agent_run(agent_name: str):
    """
    Decorator that logs agent execution to the DB.

    - Captures input state snapshot (as JSON-compatible dict).
    - Captures output state update (serialized).
    - Measures duration in milliseconds.
    - Logs any error message that occurred.
    """

    def decorator(func: AgentFn):
        @functools.wraps(func)
        def wrapper(state: FoundryState) -> StateUpdate:
            start_time = time.time()
            session_id = state.session_id
            error_msg: str | None = None

            # Snapshot of input state (can be large; acceptable for debugging)
            input_snapshot = state.model_dump(mode="json")
            output_snapshot: Dict[str, Any] = {}

            try:
                result = func(state)

                # Serialize result to JSON-compatible dict for logging
                serialized_result: Dict[str, Any] = {}
                for key, value in result.items():
                    serialized_result[key] = _serialize_value(value)

                output_snapshot = serialized_result
                return result

            except Exception as e:
                error_msg = str(e)
                raise
            finally:
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000.0

                db = None
                try:
                    db = SessionLocal()
                    run_record = AgentRun(
                        id=str(uuid4()),
                        session_id=session_id,
                        agent_name=agent_name,
                        input_snapshot=input_snapshot,
                        output_snapshot=output_snapshot,
                        duration_ms=duration_ms,
                        error=error_msg,
                    )
                    db.add(run_record)
                    db.commit()
                except Exception as log_err:
                    # Logging failures should never crash the agent
                    print(f"[log_agent_run] Failed to log agent run for {agent_name}: {log_err}")
                finally:
                    if db is not None:
                        db.close()

        return wrapper

    return decorator
