import threading
import time

from flask import current_app, request

from app.exceptions import ForbiddenError


_RATE_LIMIT_STORAGE = {}
_RATE_LIMIT_LOCK = threading.Lock()


def get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _cleanup_old_entries(now: float):
    expired_keys = [
        key
        for key, value in _RATE_LIMIT_STORAGE.items()
        if value["reset_at"] <= now
    ]

    for key in expired_keys:
        _RATE_LIMIT_STORAGE.pop(key, None)


def enforce_rate_limit(
    action: str,
    limit: int,
    window_seconds: int,
    identifier: str | None = None,
):
    if current_app.config.get("TESTING"):
        return

    now = time.time()
    client_id = identifier or get_client_ip()
    storage_key = f"{action}:{client_id}"

    with _RATE_LIMIT_LOCK:
        _cleanup_old_entries(now)

        bucket = _RATE_LIMIT_STORAGE.get(storage_key)

        if not bucket or bucket["reset_at"] <= now:
            _RATE_LIMIT_STORAGE[storage_key] = {
                "count": 1,
                "reset_at": now + window_seconds,
            }
            return

        if bucket["count"] >= limit:
            raise ForbiddenError(
                "Too many requests, try again later",
                code="rate_limit_exceeded",
            )

        bucket["count"] += 1