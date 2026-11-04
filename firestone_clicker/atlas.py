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

# Navigation. BIG_CLOSE is a dialog's X; on the main screen that spot is the settings gear.
BIG_CLOSE = Point(1851, 84)
SETTINGS_CLOSE = Point(1725, 116)
MM_SETTINGS_OPEN = Probe(1542, 655, 1654, 687, 0x285483, 3, "mm_settings_open")
DIALOG_CLOSE_X = Probe(1849, 81, 1858, 90, DIALOG_X_CROSS, 30, "dialog_close_x")
TOWN_OPEN = Probe(35, 447, 65, 465, 0xF6C100, 12, "town_open")

# Heroes (classic U menu): (config key, green-button probe rect, click point).
HERO_UPGRADE_SLOTS = (
    ("special", (1874, 207, 1889, 249), Point(1670, 205)),
    ("h5", (1868, 880, 1885, 912), Point(1670, 873)),
    ("h4", (1864, 770, 1889, 802), Point(1670, 772)),
    ("h3", (1866, 654, 1889, 693), Point(1670, 650)),
    ("h2", (1866, 545, 1885, 584), Point(1670, 539)),
    ("h1", (1862, 434, 1888, 469), Point(1670, 427)),
    ("guardian", (1869, 319, 1890, 352), Point(1670, 317)),
)
