"""Pipeline execution profiler for timing stages."""

from contextlib import contextmanager
import time
from typing import Dict, Generator
from app.utils.timer import get_timings as get_timer_timings

_profiler_timings: Dict[str, float] = {}

class PipelineProfiler:
    """Collects and aggregates timings from decorated stages and manual profile blocks."""

    @classmethod
    def reset(cls) -> None:
        """Resets all profiler recorded timings."""
        global _profiler_timings
        _profiler_timings = {}

    @classmethod
    @contextmanager
    def profile(cls, stage_name: str) -> Generator[None, None, None]:
        """Measures the execution duration of the wrapped block.

        Args:
            stage_name: Name of the profiled stage.
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            _profiler_timings[stage_name] = elapsed

    @classmethod
    def get_profile_timings(cls) -> Dict[str, float]:
        """Merges and returns timing metrics from timer.py and the manual profiler.

        Returns:
            Dict[str, float]: Timing profile dict.
        """
        merged = {}
        # Import timings from the timer stage decorator
        merged.update(get_timer_timings())
        # Overwrite/add custom profiled blocks
        merged.update(_profiler_timings)
        return merged
