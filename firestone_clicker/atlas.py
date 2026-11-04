"""Screen coordinates for Firestone at 1920x1080, game maximized (client 1920x1009 at y=31).

Logical coordinates equal screen coordinates in that setup. Constants copied from
Lutakh/firestone-bot vision/atlas.py (python-rework, fba1b7f) unless noted.
"""

from __future__ import annotations

from dataclasses import dataclass

REF_ORIGIN = (0, 31)
REF_SIZE = (1920, 1009)


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class Probe:
    """PixelSearch: inclusive rect corners (any order), colour 0xRRGGBB, per-channel variation."""

    x1: int
    y1: int
    x2: int
    y2: int
    color: int
    var: int = 3
    name: str = ""

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (
            min(self.x1, self.x2),
            min(self.y1, self.y2),
            max(self.x1, self.x2),
            max(self.y1, self.y2),
        )


# Common colours.
RED_DOT = 0xF41000
RED_DOT_VAR = 32
GREEN_BUTTON = 0x0AA008
GREEN_BUTTON_2 = 0x16BC15
ORANGE_1 = 0xF9AA47
ORANGE_2 = 0xFCAC47
IDLE_TROOP = 0x542710
AWAKEN_GREEN = 0x0A9F05
DIALOG_RING = 0xFF6109
DIALOG_X_CROSS = 0xFFF9CE
