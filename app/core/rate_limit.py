import time
from collections import defaultdict, deque

MAX_FAILED_ATTEMPTS = 5
WINDOW_SECONDS = 15 * 60

_failed_attempts: dict[str, deque] = defaultdict(deque)


def _drop_old(key: str, now: float) -> deque:
    attempts = _failed_attempts[key]
    while attempts and now - attempts[0] > WINDOW_SECONDS:
        attempts.popleft()
    return attempts


def seconds_until_allowed(key: str) -> int:
    """0 means the user may try again. Otherwise, how many seconds to wait."""
    now = time.monotonic()
    attempts = _drop_old(key, now)
    if len(attempts) < MAX_FAILED_ATTEMPTS:
        return 0
    return int(WINDOW_SECONDS - (now - attempts[0])) + 1


def record_failure(key: str) -> None:
    _failed_attempts[key].append(time.monotonic())


def clear(key: str) -> None:
    _failed_attempts.pop(key, None)


def reset_all() -> None:
    _failed_attempts.clear()
