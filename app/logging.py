import logging
import uuid

from flask import g, request


logger = logging.getLogger("gunicorn.error")

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logger = logging.getLogger()


def get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr


def get_actor():
    current_user = getattr(g, "current_user", None)

    if isinstance(current_user, dict):
        email = current_user.get("email")
        user_id = current_user.get("id")

        if email:
            return email
        if user_id is not None:
            return f"user:{user_id}"

    return "anonymous"


def get_request_id():
    if not hasattr(g, "request_id"):
        g.request_id = str(uuid.uuid4())
    return g.request_id


def build_log_context():
    return {
        "request_id": get_request_id(),
        "method": request.method,
        "path": request.path,
        "ip": get_client_ip(),
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "referer": request.headers.get("Referer", "-"),
        "actor": get_actor(),
    }


def log(level, message, **extra):
    ctx = build_log_context()
    payload = {**ctx, **extra}

    formatted = (
        f"[request_id={payload['request_id']}] "
        f"{payload['method']} {payload['path']} | "
        f"ip={payload['ip']} | "
        f"actor={payload['actor']} | "
        f"{message}"
    )

    reserved = {
        "request_id",
        "method",
        "path",
        "ip",
        "actor",
    }

    extra_parts = [
        f"{key}={value}"
        for key, value in payload.items()
        if key not in reserved
    ]

    if extra_parts:
        formatted += " | " + " | ".join(extra_parts)

    if level == "info":
        logger.info(formatted)
    elif level == "warning":
        logger.warning(formatted)
    elif level == "error":
        logger.error(formatted)
    elif level == "exception":
        logger.exception(formatted)
    else:
        logger.info(formatted)