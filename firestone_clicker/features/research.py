"""Library research, minimal: claim finished slots, start any available box in view (free only)."""

from __future__ import annotations

from firestone_clicker import atlas, nav, vision
from firestone_clicker.atlas import Point
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx

Rect = tuple[int, int, int, int]


def _centre(r: Rect) -> Point:
    return Point((r[0] + r[2]) // 2, (r[1] + r[3]) // 2)


def _park(ctx: Ctx) -> None:
    ctx.move(atlas.RS_PARK.x, atlas.RS_PARK.y)
    ctx.sleep(300)


def _done_buttons(ctx: Ctx) -> list[Rect]:
    img = ctx.grab(atlas.RS_SLOT_STRIP)
    origin = (atlas.RS_SLOT_STRIP[0], atlas.RS_SLOT_STRIP[1])
    out: list[Rect] = []
    for color in (atlas.GREEN_BUTTON, atlas.GREEN_BUTTON_2):
        out += vision.color_boxes(
            img, origin, color, atlas.RS_SLOT_DONE_VAR, atlas.RS_BUTTON_MIN_W, atlas.RS_BUTTON_MIN_H
        )
    return out


def available_boxes(ctx: Ctx) -> list[Rect]:
    img = ctx.grab(atlas.RS_TREE_AREA)
    origin = (atlas.RS_TREE_AREA[0], atlas.RS_TREE_AREA[1])
    return vision.color_boxes(
        img, origin, atlas.RS_AVAILABLE, atlas.RS_AVAILABLE_VAR, atlas.RS_BOX_MIN_W, atlas.RS_BOX_MIN_H
    )


def _slots_full(ctx: Ctx) -> bool:
    return nav.found(ctx, atlas.RS_SLOTS_FULL_X) and nav.found(ctx, atlas.RS_SLOTS_FULL_CREAM)


def _close_popup(ctx: Ctx) -> None:
    x = nav.find_dialog_x(ctx, atlas.RS_POPUP_X_BAND)
    if x is not None:
        nav.click(ctx, x, 800)
    elif nav.found(ctx, atlas.RS_POPUP_CLOSE_X):
        nav.click(ctx, atlas.RS_POPUP_CLOSE, 800)
    else:
        nav.click(ctx, atlas.RS_POPUP_OUTSIDE, 800)


def _popup_button(ctx: Ctx) -> Rect | None:
    band = atlas.RS_POPUP_BUTTON_BAND
    waited = 0
    while waited <= 2000:
        boxes = vision.green_boxes(ctx.grab(band), (band[0], band[1]), min_w=atlas.RS_POPUP_BUTTON_MIN_W)
        if boxes:
            return boxes[0]
        ctx.sleep(250)
        waited += 250
    return None


def run(ctx: Ctx, cfg: Config) -> None:
    if not nav.require_screen(ctx, atlas.TOWN_LIBRARY, via_town=True):
        return
    nav.click(ctx, atlas.RS_FIRESTONE_TREE, 1000)
    _park(ctx)
    for box in _done_buttons(ctx):
        if nav.safe_click(ctx, _centre(box), box, 1500):
            ctx.log("research: claimed")
        _park(ctx)
    for _ in range(atlas.RS_MAX_STARTS):
        if _slots_full(ctx):
            nav.click(ctx, atlas.RS_SLOTS_FULL_CLOSE, 800)
            ctx.log("research: slots full")
            break
        boxes = available_boxes(ctx)
        if not boxes:
            break
        nav.click(ctx, _centre(boxes[0]), 800)
        button = _popup_button(ctx)
        if button is None:
            ctx.log("research: no popup button")
            _close_popup(ctx)
            break
        if nav.safe_click(ctx, _centre(button), button, 1500):
            ctx.log("research: started")
        else:
            _close_popup(ctx)
            break
        _park(ctx)
    nav.big_close(ctx)
