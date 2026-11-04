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

# Guild screen.
MAIN_GUILD_ICON = Point(1857, 481)
GUILD_EXPEDITION_DOT = Probe(450, 410, 380, 490, RED_DOT, RED_DOT_VAR, "guild_expedition_dot")
GUILD_EXPEDITIONS = Point(308, 406)
GUILD_EXPEDITION_START = Point(1321, 331)
GUILD_EXPEDITION_START_RECT = (1221, 306, 1421, 356)
GUILD_PTREE_ENTRY = Point(1560, 366)

# Awakening (from the guild screen).
AWAKEN_DOT = Probe(1107, 745, 1367, 944, RED_DOT, RED_DOT_VAR, "awaken_dot")
AWAKEN_OPEN = Point(1192, 847)
AWAKEN_X1 = Point(1577, 400)
AWAKEN_BUTTON_ORANGE = Probe(1600, 566, 1845, 612, 0xF4A044, 1, "awaken_button_orange")
AWAKEN_BUTTON_GREEN = Probe(1600, 566, 1845, 612, AWAKEN_GREEN, 1, "awaken_button_green")
AWAKEN_BUTTON = Point(1725, 582)
AWAKEN_BUTTON_RECT = (1600, 566, 1845, 612)
AWAKEN_AUTO_READY = Probe(1650, 955, 1900, 1015, AWAKEN_GREEN, 1, "awaken_auto_ready")
AWAKEN_AUTO = Point(1774, 993)
AWAKEN_AUTO_RECT = (1650, 955, 1900, 1015)
AWAKEN_MULTIPLIERS = (  # highest first: (probe, button)
    (Probe(1825, 632, 1910, 692, AWAKEN_GREEN, 1, "awaken_x160"), Point(1872, 666)),
    (Probe(1727, 632, 1815, 692, AWAKEN_GREEN, 1, "awaken_x80"), Point(1772, 666)),
    (Probe(1630, 632, 1716, 692, AWAKEN_GREEN, 1, "awaken_x40"), Point(1679, 666)),
    (Probe(1535, 632, 1615, 692, AWAKEN_GREEN, 1, "awaken_x20"), Point(1577, 666)),
    (Probe(1825, 365, 1910, 423, AWAKEN_GREEN, 1, "awaken_x10"), Point(1872, 400)),
    (Probe(1727, 365, 1815, 423, AWAKEN_GREEN, 1, "awaken_x5"), Point(1772, 400)),
    (Probe(1630, 365, 1716, 423, AWAKEN_GREEN, 1, "awaken_x2"), Point(1679, 400)),
    (Probe(1535, 365, 1615, 423, AWAKEN_GREEN, 1, "awaken_x1"), Point(1577, 400)),
)

# Personal tree (from the guild screen). Measured live 2026-11-04: a node opens a blue popup
# with a green "Buy upgrade" button; without tokens a cream "You need N more Expedition
# token" popup appears whose green "Get more" overlaps the buy point, so it is probed and closed.
PTREE_OPEN = Point(1823, 945)
PTREE_POPUP = Probe(680, 430, 720, 470, 0x295484, 6, "ptree_popup")
PTREE_POPUP_CLOSE = Point(1239, 284)
PTREE_BUY = Point(960, 686)
PTREE_BUY_RECT = (840, 645, 1080, 730)
PTREE_NEED_MORE = Probe(680, 560, 720, 590, 0xFAF3E1, 8, "ptree_need_more")
PTREE_NEED_MORE_CLOSE = Point(1283, 349)
# Guardian (Magic Quarter, via town).
TOWN_MAGIC_QUARTER = Point(658, 284)
GUARDIAN_EVOLVE_DOT = Probe(1307, 107, 1346, 136, RED_DOT, RED_DOT_VAR, "guardian_evolve_dot")
GUARDIAN_EVOLVE_TAB = Point(1200, 165)
GUARDIAN_EVOLVE_BUTTON = Point(1117, 750)
GUARDIAN_EVOLVE_RECT = (1017, 725, 1217, 775)
GUARDIAN_BACK_TAB = Point(1049, 171)
GUARDIAN_TRAIN_READY = Probe(1199, 766, 1257, 810, GREEN_BUTTON, 3, "guardian_train_ready")
GUARDIAN_TRAIN_BUTTON = Point(1138, 787)
GUARDIAN_TRAIN_RECT = (1038, 762, 1238, 812)

# Alchemist (via town). Fields: idle marker, done (green), free speed-up (orange), running
# timer (brown), collect point, start point, button body rect.
TOWN_ALCHEMIST = Point(511, 837)
ALCHEMY_PARK = TOWN_ALCHEMIST
ALCHEMY_BUTTON_ORANGE_MIN = 0.15
ALCHEMY_GEM_MAX = 60 / 12950


@dataclass(frozen=True)
class AlchemySlot:
    key: str
    not_running: Probe
    complete: Probe
    free: Probe
    in_progress: Probe
    collect: Point
    start: Point
    button: tuple[int, int, int, int]


ALCHEMY_SLOTS = (
    AlchemySlot(
        "dragon_blood",
        Probe(928, 519, 948, 535, 0xFFC700, 3, "alch_blood_idle"),
        Probe(985, 746, 1037, 792, GREEN_BUTTON, 3, "alch_blood_done"),
        Probe(969, 742, 1026, 756, ORANGE_1, 3, "alch_blood_free"),
        Probe(1007, 735, 1030, 766, 0x916A38, 3, "alch_blood_running"),
        Point(949, 777),
        Point(951, 771),
        (848, 755, 1033, 825),
    ),
    AlchemySlot(
        "strange_dust",
        Probe(1274, 515, 1298, 537, 0xFFC700, 3, "alch_dust_idle"),
        Probe(1336, 748, 1386, 789, GREEN_BUTTON, 3, "alch_dust_done"),
        Probe(1336, 748, 1386, 789, ORANGE_1, 3, "alch_dust_free"),
        Probe(1346, 734, 1373, 766, 0x916A38, 3, "alch_dust_running"),
        Point(1286, 786),
        Point(1286, 786),
        (1196, 755, 1381, 825),
    ),
    AlchemySlot(
        "exotic_coins",
        Probe(1622, 518, 1645, 538, 0xFFC700, 3, "alch_coin_idle"),
        Probe(1679, 748, 1735, 796, GREEN_BUTTON, 3, "alch_coin_done"),
        Probe(1679, 748, 1735, 796, ORANGE_1, 3, "alch_coin_free"),
        Probe(1699, 737, 1723, 767, 0x916A38, 3, "alch_coin_running"),
        Point(1632, 772),
        Point(1641, 767),
        (1544, 755, 1729, 825),
    ),
)

# Research (library, via town). Minimal: claim green slot buttons, start any available box.
TOWN_LIBRARY = Point(329, 657)
RS_FIRESTONE_TREE = Point(1816, 610)
RS_PARK = Point(1300, 60)
RS_SLOT_STRIP = (60, 880, 1450, 1010)
RS_SLOT_DONE_VAR = 25
RS_SLOT_COUNT = 2
RS_BUTTON_MIN_W = 40
RS_BUTTON_MIN_H = 25
RS_TREE_AREA = (40, 110, 1725, 860)
RS_AVAILABLE = 0x1D49DE
RS_AVAILABLE_VAR = 32
RS_BOX_MIN_W = 140
RS_BOX_MIN_H = 60
RS_POPUP_BUTTON_BAND = (620, 630, 980, 860)
RS_POPUP_BUTTON_MIN_W = 200
RS_POPUP_X_BAND = (1170, 160, 1300, 340)
RS_POPUP_CLOSE_X = Probe(1215, 200, 1263, 248, DIALOG_RING, 30, "rs_popup_close_x")
RS_POPUP_CLOSE = Point(1239, 224)
RS_POPUP_OUTSIDE = Point(100, 150)
RS_SLOTS_FULL_X = Probe(1346, 331, 1394, 379, DIALOG_RING, 30, "rs_slots_full_x")
RS_SLOTS_FULL_CREAM = Probe(1090, 641, 1110, 661, 0xE8D1B7, 25, "rs_slots_full_cream")
RS_SLOTS_FULL_CLOSE = Point(1370, 355)
RS_MAX_STARTS = 2

# World map missions (M key). The map must stay at its default position and zoom.
MR_FREE_RESET = Probe(221, 878, 277, 891, ORANGE_2, 3, "mr_free_reset")
MR_FREE_RESET_BUTTON = Point(173, 918)
MR_REFRESH_RECT = (95, 869, 297, 976)
MR_NO_MISSIONS = Probe(117, 249, 208, 334, 0x1452B4, 3, "mr_no_missions")
MR_MISSION_DONE = Probe(207, 305, 244, 348, GREEN_BUTTON, 3, "mr_mission_done")
MR_FIRST_MISSION = Point(162, 334)
MAP_POPUP_BAND = (300, 150, 1620, 900)
# Every map popup's X sits top-right; searching the whole band matched the mission avatar's
# orange ring at (971,246) instead and left the popup open (2026-11-04).
MAP_POPUP_X_BAND = (1380, 160, 1620, 330)
MAP_POPUP_OUTSIDE = Point(1700, 540)
MAP_MAX_COLLECT = 10
MAP_MAX_STARTS = 15
# Measured live 2026-11-04. "Your squads are idling!" banner at the bottom (brown text) means
# a squad is free. An available mission is a scroll icon with a teal ring; in-progress icons
# are pink (sword) or green (telescope). The reference bot's fixed spot list did not line up.
MAP_IDLE_BANNER = Probe(600, 992, 1100, 1008, IDLE_TROOP, 10, "map_idle_banner")
MAP_ICON_AREA = (300, 100, 1700, 940)
# (colour, variation, min box px): pink sword circle, cyan scroll ring, orange dragon body,
# orange telescope (expedition) body.
MAP_ICON_COLORS = ((0xF07070, 24, 30), (0x00A8B0, 28, 12), (0xF87800, 20, 12), (0xF8A860, 20, 12))
MAP_ICON_MERGE = 45

# Oracle rituals (via town). Measured live 2026-11-04: four cards in a 2x2 grid, each with
# one button: grey "Claimed", green "Start" (free), green "Claim", or a timer while running.
TOWN_ORACLE = Point(1023, 994)
ORACLE_RITUALS_TAB = Point(828, 436)
ORACLE_RITUAL_BUTTONS = (
    (985, 470, 1355, 548),
    (1390, 470, 1760, 548),
    (985, 812, 1355, 890),
    (1390, 812, 1760, 890),
)
ORACLE_POPUP_BAND = (700, 560, 1250, 760)  # a reward popup's Okay lands here, between the card rows

PTREE_NODES = (
    ("AttDmg", Point(365, 313)),
    ("AttHp", Point(512, 276)),
    ("AttArm", Point(687, 367)),
    ("Energy", Point(353, 492)),
    ("Mana", Point(511, 442)),
    ("Rage", Point(687, 534)),
    ("Miner", Point(858, 199)),
    ("Battle", Point(1061, 205)),
    ("MainAtt", Point(957, 365)),
    ("Prest", Point(963, 536)),
    ("Fire", Point(860, 696)),
    ("Gold", Point(1059, 701)),
    ("Level", Point(849, 866)),
    ("Guard", Point(1063, 867)),
    ("Fist", Point(1235, 369)),
    ("Prec", Point(1399, 276)),
    ("Magic", Point(1567, 320)),
    ("Tank", Point(1233, 535)),
    ("Damage", Point(1404, 440)),
    ("Heal", Point(1572, 492)),
)
