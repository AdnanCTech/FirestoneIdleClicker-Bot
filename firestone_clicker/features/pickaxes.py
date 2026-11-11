"""Free pickaxes: guild > Guild market > Supplies, press the green Claim on the free card.

The free pickaxes accumulate and one click claims them all, so a visit per schedule window
is enough. The two other cards are paid (orange, arena tokens) and are never touched.
"""

from __future__ import annotations

from firestone_clicker import atlas, nav, vision
from firestone_clicker.atlas import Point
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx

Rect = tuple[int, int, int, int]


def _centre(r: Rect) -> Point:
    return Point((r[0] + r[2]) // 2, (r[1] + r[3]) // 2)


def claim_button(ctx: Ctx) -> Rect | None:
    band = atlas.PICK_CLAIM_BAND
    boxes = vision.green_boxes(ctx.grab(band), (band[0], band[1]), min_w=atlas.PICK_CLAIM_MIN_W)
    return boxes[0] if boxes else None


def run(ctx: Ctx, cfg: Config) -> bool:
    """True when the Supplies tab was checked (claimed or nothing to claim); False to retry."""
    if not nav.require_screen(ctx, atlas.MAIN_GUILD_ICON):
        return False
    if not nav.require_screen(ctx, atlas.PICK_MARKET, atlas.PICK_MARKET_OPEN):
        nav.big_close(ctx)
        return False
    if not nav.require_screen(ctx, atlas.PICK_SUPPLIES, atlas.PICK_SUPPLIES_OPEN):
        nav.big_close(ctx)
        nav.big_close(ctx)
        return False
    button = claim_button(ctx)
    if button is None:
        ctx.log("pickaxes: nothing to claim")
    elif nav.safe_click(ctx, _centre(button), button, 1500):
        ctx.log("pickaxes: claimed")
    nav.big_close(ctx)
    nav.big_close(ctx)
    return True
