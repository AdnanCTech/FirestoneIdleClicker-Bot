"""Oracle rituals: press every green card button (Claim or Start, both free), gem-gated."""

from __future__ import annotations

from firestone_clicker import atlas, nav, vision
from firestone_clicker.atlas import Point
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx

Rect = tuple[int, int, int, int]


def _centre(r: Rect) -> Point:
    return Point((r[0] + r[2]) // 2, (r[1] + r[3]) // 2)


def _green_in(ctx: Ctx, rect: Rect, min_w: int = 100) -> Rect | None:
    boxes = vision.green_boxes(ctx.grab(rect), (rect[0], rect[1]), min_w=min_w)
    return boxes[0] if boxes else None


def run(ctx: Ctx, cfg: Config) -> None:
    if not nav.require_screen(ctx, atlas.TOWN_ORACLE, via_town=True):
        return
    nav.click(ctx, atlas.ORACLE_RITUALS_TAB, 1500)
    for i, rect in enumerate(atlas.ORACLE_RITUAL_BUTTONS):
        ctx.move(300, 540)  # off the panel so no hover highlight skews the colours
        ctx.sleep(200)
        button = _green_in(ctx, rect)
        if button is None:
            continue
        if nav.safe_click(ctx, _centre(button), button, 1500):
            ctx.log(f"oracle: ritual {i + 1} button pressed")
            okay = _green_in(ctx, atlas.ORACLE_POPUP_BAND, min_w=150)
            if okay is not None:
                nav.safe_click(ctx, _centre(okay), okay, 1200)
    nav.big_close(ctx)
