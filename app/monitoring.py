import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default

    try:
        parsed = float(value)
    except ValueError:
        return default

    if parsed < 0:
        return 0.0
    if parsed > 1:
        return 1.0
    return parsed


def init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return

    app_env = os.getenv("APP_ENV", "development").lower()

    traces_sample_rate = _get_float_env(
        "SENTRY_TRACES_SAMPLE_RATE",
        0.0 if app_env == "production" else 1.0,
    )

    profiles_sample_rate = _get_float_env(
        "SENTRY_PROFILES_SAMPLE_RATE",
        0.0,
    )

    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration()],
        environment=os.getenv("SENTRY_ENVIRONMENT", app_env),
        release=os.getenv("SENTRY_RELEASE"),
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        send_default_pii=False,
        debug=app_env != "production",
    )