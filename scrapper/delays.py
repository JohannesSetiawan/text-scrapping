"""Rate-limit helpers: jittered delays and exponential backoff."""

import random
import time


def jittered_sleep(min_seconds: float, max_seconds: float) -> float:
    """Sleep for a random duration within [min_seconds, max_seconds]."""
    duration = random.uniform(min_seconds, max_seconds)
    time.sleep(duration)
    return duration


def backoff_sleep(attempt: int, base_seconds: float = 1.0) -> float:
    """Sleep using exponential backoff plus jitter for a given retry attempt."""
    duration = base_seconds * (2 ** attempt) + random.uniform(0.0, 0.5)
    time.sleep(duration)
    return duration
