"""Reusable timing utilities for tracking execution times of pipeline stages."""

import time
import functools
import threading
from typing import Callable, Dict

_local = threading.local()

def get_timings() -> Dict[str, float]:
    """Retrieves current thread-local execution timings.

    Returns:
        Dict[str, float]: Dictionary mapping stage names to elapsed execution times (seconds).
    """
    if not hasattr(_local, "timings"):
        _local.timings = {}
    return _local.timings

def reset_timings() -> None:
    """Resets thread-local execution timings."""
    _local.timings = {}

def time_stage(stage_name: str) -> Callable:
    """Decorator to measure and log the execution time of a pipeline stage.

    Args:
        stage_name: The name of the pipeline stage.

    Returns:
        Callable: The decorated function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from app.utils.logger import get_logger
            log = get_logger(func.__module__)
            log.info(f"Starting: {stage_name}")
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start_time
                get_timings()[stage_name] = elapsed
                log.info(f"Finished: {stage_name} in {elapsed:.4f}s")
        return wrapper
    return decorator
