from __future__ import annotations

from typing import Optional

import sentry_sdk


def init_sentry(dsn: Optional[str]) -> None:
    if dsn:
        sentry_sdk.init(dsn=dsn, traces_sample_rate=0.1)
