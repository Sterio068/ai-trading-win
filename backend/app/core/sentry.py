from __future__ import annotations

import sentry_sdk

from .env import get_env_value


def init_sentry() -> None:
    dsn = get_env_value("SENTRY_DSN", "")
    if not dsn:
        return
    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=0.2,
        profiles_sample_rate=0.0,
    )


def capture_message(message: str, **tags: str) -> None:
    if not sentry_sdk.Hub.current.client:
        return
    with sentry_sdk.push_scope() as scope:
        for key, value in tags.items():
            scope.set_tag(key, value)
        sentry_sdk.capture_message(message)


def capture_exception(exc: Exception, **tags: str) -> None:
    if not sentry_sdk.Hub.current.client:
        return
    with sentry_sdk.push_scope() as scope:
        for key, value in tags.items():
            scope.set_tag(key, value)
        sentry_sdk.capture_exception(exc)


__all__ = ["init_sentry", "capture_message", "capture_exception"]
