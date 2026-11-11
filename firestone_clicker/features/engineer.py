"""Engineer tools: town > Engineer > left "Engineer" card, press the "Tools production" Claim.

Like the campaign loot it fills every 6 hours and does not stack, so each schedule window
retries every cycle until the grey Claim (showing the countdown) has turned green and was pressed.
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
    band = atlas.ENG_CLAIM_BAND
    boxes = vision.green_boxes(ctx.grab(band), (band[0], band[1]), min_w=atlas.ENG_CLAIM_MIN_W)
    return boxes[0] if boxes else None


def run(ctx: Ctx, cfg: Config) -> bool:
    """True once the tools were claimed; False while the timer still runs (retry next cycle)."""
    if not nav.require_screen(ctx, atlas.ENG_BUILDING, atlas.ENG_POPUP_X, via_town=True):
        return False
    if not nav.require_screen(ctx, atlas.ENG_CARD, atlas.ENG_OPEN):
        nav.big_close(ctx, 800)
        return False
    button = claim_button(ctx)
    claimed = False
    if button is None:
        ctx.log("engineer: not ready")
    elif nav.safe_click(ctx, _centre(button), button, 1500):
        ctx.log("engineer: claimed")
        claimed = True
    nav.big_close(ctx, 800)
    nav.big_close(ctx, 800)
    return claimed
