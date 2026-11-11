"""Run-once-per-window bookkeeping for features that only matter a few times a day.

A window is named by its start, the latest configured hour at or before now (crossing
midnight when needed). `State` keeps the windows each feature finished in state.json so a
restart does not repeat a day's arena fights.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path


def window(hours: list[int], now: datetime) -> str:
    """Name of the window `now` falls in, e.g. "2026-11-11 13" for hours [1, 13] at 13:05."""
    past = [h for h in sorted(hours) if h <= now.hour]
    if past:
        return f"{now:%Y-%m-%d} {past[-1]:02d}"
    yesterday = now - timedelta(days=1)
    return f"{yesterday:%Y-%m-%d} {max(hours):02d}"


class State:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict[str, str] = {}
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                self.data = {str(k): str(v) for k, v in loaded.items()}
        except (OSError, ValueError):
            pass  # a missing or damaged file just starts the bookkeeping over

    def done(self, name: str, win: str) -> bool:
        return self.data.get(name) == win

    def mark(self, name: str, win: str) -> None:
        self.data[name] = win
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
