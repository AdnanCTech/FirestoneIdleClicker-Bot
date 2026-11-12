"""Market (main screen): claim the free Mystery box on the first tab, then Check In on the calendar.

Both reset once a day and neither click opens a popup: the Free button turns into a grey
"Claimed" card with a countdown, the Check In button turns grey with a "Next Check in" timer.
"""

from __future__ import annotations

from firestone_clicker import atlas, nav, vision
from firestone_clicker.atlas import Point
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx

Rect = tuple[int, int, int, int]


def _centre(r: Rect) -> Point:
    return Point((r[0] + r[2]) // 2, (r[1] + r[3]) // 2)


def free_button(ctx: Ctx) -> Rect | None:
    band = atlas.MARKET_FREE_BAND
    boxes = vision.green_boxes(ctx.grab(band), (band[0], band[1]), min_w=atlas.MARKET_FREE_MIN_W)
    return boxes[0] if boxes else None


def checkin_button(ctx: Ctx) -> Rect | None:
    band = atlas.MARKET_CHECKIN_BAND
    boxes = vision.color_boxes(
        ctx.grab(band), (band[0], band[1]), atlas.MARKET_CHECKIN_BUTTON, 30,
        atlas.MARKET_CHECKIN_MIN_W, 25,
    )
    return boxes[0] if boxes else None


def run(ctx: Ctx, cfg: Config) -> bool:
    """True when both tabs were checked (claimed or already done); False to retry next cycle."""
    if not nav.require_screen(ctx, atlas.MARKET_BUTTON, atlas.MARKET_OPEN):
        return False
    button = free_button(ctx)
    if button is None:
        ctx.log("market: free box already claimed")
    elif nav.safe_click(ctx, _centre(button), button, 1500):
        ctx.log("market: free box claimed")
    if not nav.require_screen(ctx, atlas.MARKET_CHECKIN_TAB, atlas.MARKET_CHECKIN_OPEN):
        nav.big_close(ctx)
        return False
    button = checkin_button(ctx)
    if button is None:
        ctx.log("market: already checked in")
    elif nav.safe_click(ctx, _centre(button), button, 1500):
        ctx.log("market: checked in")
    nav.big_close(ctx)
    return True
