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
RS_BOX_MIN_W = 300  # boxes are 375-383 wide; one cut by the side panel at x 1725 is narrower
RS_BOX_MIN_H = 60
# Progress bar inside a box, live 2026-11-06 (box 103 tall: bar rows 70..88, x from +100 to
# -15): yellow fill 0xEFCF23, dark track 0x172874 (box body 0x193674 is 14 off in green, so
# the track variation stays tight). Columns are ~455 px apart; blobs within RS_COLUMN_GAP of
# the rightmost box's left edge belong to the same column.
RS_BAR_ROWS = (0.68, 0.85)
RS_BAR_INSET = (100, 15)
RS_BAR_FILL = (0xEFCF2C, 24)
RS_BAR_TRACK = (0x172874, 12)
RS_COLUMN_GAP = 60
RS_LOCKED = (0x919DB2, 20)  # flat grey of a "Locked" box; everything right of one is locked too
RS_RUNNING_BUTTON = (0xED913F, 24)  # orange "Speed up" in a busy slot of the strip (live 2026-11-06)
# The tree pans by dragging and keeps its position when reopened (live 2026-11-06: a 455 px
# drag moved it ~520 px, columns are ~465 px apart). Drags run along y 840, an empty band
# between the lowest box row and the slot strip, so a drag can never land on a box.
RS_DRAG_Y = 840
RS_DRAG_X = (900, 445)
RS_MAX_DRAGS = 6
RS_VIEW_CHANGE = 0.02  # share of tree pixels that must change for a drag to count as a pan
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
# a squad is free. Icons with red wings are in progress; icons with a countdown are startable
# (the countdown is how long they stay on offer). The reference bot's fixed spot list did not
# line up.
MAP_IDLE_BANNER = Probe(600, 992, 1100, 1008, IDLE_TROOP, 10, "map_idle_banner")
MAP_ICON_AREA = (300, 100, 1770, 975)  # Celenis dragon stand at x 1716; side buttons from 1775
# The idle banner is a cream gradient whose lower rows match the stand colour, and it moves
# (top at y 944 on 2026-11-06, 971 the day before). Its top is found on the column below
# "Your" and the icon scan stops there.
MAP_BANNER_COLUMN = 480
MAP_BANNER_FACE = (0xF2DEC4, 24)
# Every mission icon (sword, telescope, scroll, dragon, naval wheel, monster paw, ...) sits on
# the same small beige pin stand, so the stand is the anchor; per-type disc colours missed the
# wheel (sea blue) and paw (Dreadland purple). (colour, variation, min px). The click point is
# MAP_ICON_ABOVE_STAND px above the stand's top: the disc centre for winged icons, the countdown
# label for the others (centre 65 above). 50 sat under the animated flags of a winged neighbour
# and opened the wrong popup 1 time in 3; 35 was 10 for 10 (live 2026-11-04).
MAP_ICON_STAND = (0xE6DDB5, 16, 8)
# A stand is at least this wide and tall; a shorter one counts only when it touches the bottom
# of the scan area, where the "squads are idling" banner hides the rest of it (the naval icon
# at y 964 lost all but 7 rows). Smaller specks (mountain highlights) are dropped.
# A stand is a downward triangle, 16-20 px wide at its top row and ~100 px in all (live
# 2026-11-06). The cell grid trims its tail unpredictably, so blobs are checked by real
# pixels: (min top-row width, min matching px). A 7x7 speck has 49 px, 7 wide.
MAP_ICON_STAND_SHAPE = (13, 50)
MAP_ICON_ABOVE_STAND = 35
# Game names per icon: scope = Scout, scroll = Adventure, sword = War, paw = Monster,
# dragon = Dragon, wheel = Naval, volcano = Titan.
# Icon kind from a 28x50 window above the stand (half width, from, to px above the stand top),
# so the owner's preferred missions are opened first. (kind, ((colour, variation, min px), ...)):
# every key of a kind must match, kinds checked in this order. Measured live 2026-11-04 on four
# maps: paw magenta glow ~150 px vs 0 on every other icon, wheel cyan highlights 96 vs <=3,
# dragon deep orange 55+ vs <=2. Titan (volcano, live 2026-11-12 on Fire Island top right):
# deep blue sky in the disc's top rows 93 px vs <=3 elsewhere, plus lava orange 93 px (the
# dragon has 106 of that orange but no sky). It sits over the sea, so the wheel's cyan key
# also matches it (85 px) and the titan is checked first.
MAP_ICON_SAMPLE = (14, 75, 25)
MAP_ICON_KINDS = (
    ("titan", ((0x005090, 24, 40), (0xF08000, 30, 50))),
    ("paw", ((0xF060F0, 48, 40),)),
    ("wheel", ((0x18B8F0, 24, 30),)),
    ("dragon", ((0xF05800, 12, 25),)),
)
MAP_PRIORITY = ("titan", "paw", "wheel", "dragon")
MAP_ICON_MERGE = 45
# Panning (live 2026-11-12): the world is about three screens tall (Doomfire Island above the
# continent, Trinity Islands below) and wider than one screen; a 900 px horizontal drag slid the
# continent 700 px. The view keeps its position between opens and clamps at the edges, where a
# drag leaves the capture unchanged (0.000 of the icon area; a real pan over sea gave 0.08+).
# The idle banner shows only while a mission with enough free squads exists somewhere, so a
# banner that outlives the visible pass means one is off screen and the map is swept from the
# top-left corner. Drags start on a candidate point at least MAP_PAN_CLEAR px from every icon
# (a press on an icon could open its popup); a pointer release elsewhere clicks nothing.
MAP_PAN = {"up": (0, 600), "down": (0, -600), "left": (1000, 0), "right": (-1000, 0)}  # drag vector
MAP_PAN_STARTS = {
    "up": tuple((x, 250) for x in (380, 700, 1000, 1300, 1600)),
    "down": tuple((x, 850) for x in (380, 700, 1000, 1300, 1600)),
    "left": tuple((380, y) for y in (550, 250, 850)),
    "right": tuple((1600, y) for y in (550, 250, 850)),
}
MAP_PAN_CLEAR = 80
MAP_PAN_MAX = 4  # drags per direction before the edge is assumed
MAP_VIEW_CHANGE = 0.03  # share of icon-area pixels that must change for a drag to count as a pan
MAP_SWEEP_COOLDOWN_S = 1800  # after a sweep that started nothing (a mission the bot cannot start)

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

# Arena of Kings (town, Battles, right card). Measured live 2026-11-11. Three opponents sit
# strongest to weakest left to right; the top counter is attempts left today (resets ~9am).
ARENA_BATTLES = Point(355, 317)
ARENA_BATTLES_X = Probe(1310, 252, 1320, 262, DIALOG_X_CROSS, 30, "arena_battles_x")
ARENA_CARD = Point(1145, 532)
ARENA_OPEN = Probe(1540, 880, 1580, 895, 0x0D87FF, 30, "arena_open")  # blue "Battle log"
ARENA_CLOSE = Point(1800, 142)  # the arena's own X; BIG_CLOSE is not on this screen
ARENA_FIGHT_BAND = (560, 615, 1360, 675)
ARENA_FIGHT_MIN_W = 120
ARENA_BATTLE = Point(960, 582)  # red crossed-swords button of the battle window
ARENA_BATTLE_RECT = (880, 502, 1040, 662)
ARENA_BATTLE_BUTTON = Probe(910, 577, 930, 587, 0xD34429, 30, "arena_battle_button")
ARENA_OK_BAND = (600, 700, 1320, 860)  # green OK of the result popup (833..1086 x 753..816)
ARENA_POPUP_X_BAND = (1100, 150, 1700, 450)
ARENA_MAX_FIGHTS = 5
ARENA_OPEN_MS = 5000
ARENA_FIGHT_MAX_MS = 180000  # the longest fight seen took about 2 minutes
ARENA_POLL_MS = 3000
# Cream panel right of the "N/5" counter; at 0/5 a green "+" covers it (seen dimmed under the
# token popup only, so the probe looks for the cream, not the green).
ARENA_HAS_ATTEMPTS = Probe(1447, 147, 1457, 157, 0xDCC0A5, 20, "arena_has_attempts")

# Free pickaxes (guild > Guild market > Supplies). Measured live 2026-11-11. The market opens
# on a paid bundle tab, so Supplies is always clicked first; its tab turns dark brown.
PICK_MARKET = Point(630, 365)
PICK_MARKET_OPEN = Probe(160, 471, 180, 491, 0xBFB095, 20, "pick_market_open")  # left nav strip
PICK_SUPPLIES = Point(115, 752)
PICK_SUPPLIES_OPEN = Probe(240, 741, 260, 761, 0x433018, 20, "pick_supplies_open")
PICK_CLAIM_BAND = (540, 700, 890, 800)  # green Claim (590..838 x 721..776); grey once claimed
PICK_CLAIM_MIN_W = 150

# Daily missions (town > Battles > Campaign > "Daily missions"). Measured live 2026-11-11.
# Both the Dungeon and the Liberation window share the X spot; the Daily popup's X is lower left.
DM_CAMPAIGN = Point(773, 532)  # left card of the Battles popup
DM_CAMPAIGN_OPEN = Probe(1700, 975, 1860, 1000, GREEN_BUTTON, 30, "dm_campaign_open")  # "Daily missions"
DM_DAILY = Point(1783, 989)
DM_DAILY_X = Probe(1470, 114, 1480, 124, DIALOG_X_CROSS, 30, "dm_daily_x")
DM_DAILY_CLOSE = Point(1475, 119)
DM_LIBERATION = Point(698, 799)  # the two "Open" buttons of the Daily missions popup
DM_DUNGEON = Point(1220, 799)
DM_WINDOW_X = Probe(1758, 90, 1768, 100, DIALOG_X_CROSS, 30, "dm_window_x")
DM_WINDOW_CLOSE = Point(1763, 95)
DM_FIGHT_BAND = (140, 740, 1795, 800)  # Fight/Liberate buttons, 260 px wide; "Requires x319" has none
DM_FIGHT_MIN_W = 150
DM_DUNGEON_FIGHTS = 2
DM_STRIP_AREA = (140, 170, 1795, 860)
DM_DRAG_Y = 381  # across the card pictures
DM_DRAG_X = (1500, 500)
DM_MAX_DRAGS = 8
DM_MAX_FIGHTS = 15
DM_VIEW_CHANGE = 0.02

# Campaign loot: "Next loot" panel bottom left of the Campaign map, Claim at 35..250 x 936..1001
# (grey while the 6 h timer runs; the green state is assumed GREEN_BUTTON, unseen 2026-11-11).
CL_CLAIM_BAND = (30, 930, 260, 1005)
CL_CLAIM_MIN_W = 150

# Engineer tools (town > Engineer > left card). Measured live 2026-11-11. The "Tools production"
# Claim at 1530..1750 x 666..751 is grey with a countdown while the 6 h timer runs (green unseen).
ENG_BUILDING = Point(1262, 910)
ENG_POPUP_X = Probe(1482, 251, 1492, 261, DIALOG_X_CROSS, 30, "eng_popup_x")
ENG_CARD = Point(600, 532)
ENG_OPEN = Probe(1740, 346, 1760, 356, 0xE1CEAD, 20, "eng_open")  # beige of the effects panel
ENG_CLAIM_BAND = (1520, 660, 1760, 755)
ENG_CLAIM_MIN_W = 150

# Market (main screen, right edge). Measured live 2026-11-12. Tab 1 opens by itself with the free
# Mystery box (green Free at 551..796 x 850..901, grey "Claimed" + countdown after) next to a
# $4.99 orange bundle; the last tab (calendar) has "Check In" in a lighter green gradient
# (0x58A637..0x318A18) that GREEN_BUTTON does not match. Neither click opens a popup.
MARKET_BUTTON = Point(1860, 601)
MARKET_OPEN = Probe(290, 206, 310, 226, 0x7E82EC, 20, "market_open")  # lavender title band
MARKET_FREE_BAND = (540, 840, 810, 910)
MARKET_FREE_MIN_W = 150
MARKET_CHECKIN_TAB = Point(1385, 126)
MARKET_CHECKIN_OPEN = Probe(585, 571, 615, 591, 0xF2C65A, 25, "market_checkin_open")  # yellow page arrow
MARKET_CHECKIN_BAND = (1240, 805, 1450, 865)
MARKET_CHECKIN_BUTTON = 0x45981F
MARKET_CHECKIN_MIN_W = 100

# Oracle's gift (town > Oracle > Market tab). Measured live 2026-11-12. Same layout as the main
# Market: green Free at 571..817 x 771..821 beside a $4.99 orange bundle, grey "Claimed" +
# countdown after, no popup. The X of the market returns to the Oracle screen.
ORACLE_MARKET_TAB = Point(828, 771)
ORACLE_MARKET_OPEN = Probe(160, 201, 180, 221, 0x23354A, 20, "oracle_market_open")  # navy side panel
ORACLE_GIFT_BAND = (560, 771, 830, 826)
ORACLE_GIFT_MIN_W = 150
