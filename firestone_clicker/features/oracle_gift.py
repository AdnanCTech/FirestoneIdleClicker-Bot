"""Oracle's gift: town > Oracle > Market tab, press the green Free on the gift card.

Resets once a day; the click claims with no popup and the card turns grey with a countdown.
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
    band = atlas.ORACLE_GIFT_BAND
    boxes = vision.green_boxes(ctx.grab(band), (band[0], band[1]), min_w=atlas.ORACLE_GIFT_MIN_W)
    return boxes[0] if boxes else None


def run(ctx: Ctx, cfg: Config) -> bool:
    """True when the gift card was checked (claimed or already done); False to retry next cycle."""
    if not nav.require_screen(ctx, atlas.TOWN_ORACLE, via_town=True):
        return False
    if not nav.require_screen(ctx, atlas.ORACLE_MARKET_TAB, atlas.ORACLE_MARKET_OPEN):
        nav.big_close(ctx)
        return False
    button = free_button(ctx)
    if button is None:
        ctx.log("oracle gift: already claimed")
    elif nav.safe_click(ctx, _centre(button), button, 1500):
        ctx.log("oracle gift: claimed")
    nav.big_close(ctx)  # market -> oracle
    nav.big_close(ctx)  # oracle -> town
    return True
