"""Run-once-per-window bookkeeping for features that only matter a few times a day.

A window is named by its start, the latest configured hour at or before now (crossing
midnight when needed). `State` keeps the windows each feature finished in state.json so a
restart does not repeat a day's arena fights. Features with a cooldown that starts at the claim
(loot, engineer) store the claim time instead and are `due` once `every_h` hours have passed.
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


def due(last: str | None, every_h: int, now: datetime) -> bool:
    """True when `last` (ISO claim time) is missing, unreadable or at least every_h hours ago.
    A window name from before every_h ("2026-11-14 07") parses as that hour, a fair anchor."""
    if last is None:
        return True
    try:
        then = datetime.fromisoformat(last)
    except ValueError:
        return True
    return now - then >= timedelta(hours=every_h)


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

    def last(self, name: str) -> str | None:
        return self.data.get(name)

    def mark(self, name: str, win: str) -> None:
        self.data[name] = win
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
