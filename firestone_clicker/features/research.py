"""Library research: claim finished slots, pan the tree to its right end and start the
available box in the rightmost open column with the least progress (free only)."""

from __future__ import annotations

import numpy as np

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
    # GREEN_BUTTON ±25 already covers GREEN_BUTTON_2; a second colour duplicated every box.
    img = ctx.grab(atlas.RS_SLOT_STRIP)
    origin = (atlas.RS_SLOT_STRIP[0], atlas.RS_SLOT_STRIP[1])
    return vision.color_boxes(
        img, origin, atlas.GREEN_BUTTON, atlas.RS_SLOT_DONE_VAR, atlas.RS_BUTTON_MIN_W, atlas.RS_BUTTON_MIN_H
    )


def available_boxes(ctx: Ctx) -> list[Rect]:
    # Connected blobs, not column projection: the box's title text and progress bar leave too
    # few pure-blue rows for the projection to accept it (live 2026-11-04).
    img = ctx.grab(atlas.RS_TREE_AREA)
    origin = (atlas.RS_TREE_AREA[0], atlas.RS_TREE_AREA[1])
    return vision.blobs(img, origin, atlas.RS_AVAILABLE, atlas.RS_AVAILABLE_VAR, atlas.RS_BOX_MIN_H)


def _bar_fill(img, origin: tuple[int, int], box: Rect) -> float:
    """Share of the box's progress bar that is filled (0.0 when the bar is not found)."""
    x1, y1, x2, y2 = box
    r1, r2 = atlas.RS_BAR_ROWS
    left, right = atlas.RS_BAR_INSET
    h = y2 - y1
    band = img[y1 - origin[1] + int(h * r1) : y1 - origin[1] + int(h * r2), x1 - origin[0] + left : x2 - origin[0] - right]
    fill = int(vision.match_mask(band, *atlas.RS_BAR_FILL).sum())
    track = int(vision.match_mask(band, *atlas.RS_BAR_TRACK).sum())
    return fill / (fill + track) if fill + track else 0.0


def pick_box(ctx: Ctx) -> Rect | None:
    """The available box to start: rightmost column first (columns unlock on levels in the
    one before), then the lowest progress bar, then top to bottom."""
    img = ctx.grab(atlas.RS_TREE_AREA)
    origin = (atlas.RS_TREE_AREA[0], atlas.RS_TREE_AREA[1])
    boxes = vision.blobs(img, origin, atlas.RS_AVAILABLE, atlas.RS_AVAILABLE_VAR, atlas.RS_BOX_MIN_H)
    boxes = [b for b in boxes if b[2] - b[0] >= atlas.RS_BOX_MIN_W]
    if not boxes:
        return None
    right = max(b[0] for b in boxes)
    column = [b for b in boxes if right - b[0] <= atlas.RS_COLUMN_GAP]
    return min(column, key=lambda b: (round(_bar_fill(img, origin, b), 2), b[1]))


def _drag(ctx: Ctx, to_right_end: bool) -> np.ndarray:
    """Pan the tree one column (towards its right end, or back) and return the new view."""
    a, b = atlas.RS_DRAG_X
    if to_right_end:
        ctx.drag(a, atlas.RS_DRAG_Y, b, atlas.RS_DRAG_Y)
    else:
        ctx.drag(b, atlas.RS_DRAG_Y, a, atlas.RS_DRAG_Y)
    _park(ctx)
    ctx.sleep(500)  # the pan glides to a stop
    return ctx.grab(atlas.RS_TREE_AREA)


def _changed(before: np.ndarray, after: np.ndarray) -> bool:
    diff = np.abs(before[:, :, :3].astype(np.int16) - after[:, :, :3].astype(np.int16)).max(axis=2) > 40
    return float(diff.mean()) > atlas.RS_VIEW_CHANGE


def _scroll_to_end(ctx: Ctx) -> None:
    view = ctx.grab(atlas.RS_TREE_AREA)
    for _ in range(atlas.RS_MAX_DRAGS):
        after = _drag(ctx, to_right_end=True)
        if not _changed(view, after):
            return
        view = after


def _find_box(ctx: Ctx) -> Rect | None:
    """The box to start at the right end of the tree, else one column back at a time."""
    box = pick_box(ctx)
    for _ in range(atlas.RS_MAX_DRAGS):
        if box is not None:
            return box
        _drag(ctx, to_right_end=False)
        box = pick_box(ctx)
    return box


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
    # Re-detect after every claim: the strip re-lays out and the next button moves.
    claimed = 0
    for _ in range(atlas.RS_SLOT_COUNT * 2):
        done = _done_buttons(ctx)
        if not done:
            break
        if nav.safe_click(ctx, _centre(done[0]), done[0], 1500):
            ctx.log("research: claimed")
            claimed += 1
        else:
            break
        _park(ctx)
    if not claimed:
        ctx.log("research: no finished slot")
    started = 0
    scrolled = False
    for _ in range(atlas.RS_MAX_STARTS):
        if _slots_full(ctx):
            nav.click(ctx, atlas.RS_SLOTS_FULL_CLOSE, 800)
            ctx.log("research: slots full")
            break
        if not scrolled:
            _scroll_to_end(ctx)
            scrolled = True
        box = _find_box(ctx)
        if box is None:
            ctx.log(f"research: no available box, {started} started")
            break
        ctx.log(f"research: starting box at {box[0]},{box[1]}")
        nav.click(ctx, _centre(box), 800)
        button = _popup_button(ctx)
        if button is None:
            ctx.log("research: no popup button")
            _close_popup(ctx)
            break
        if not nav.safe_click(ctx, _centre(button), button, 1500):
            _close_popup(ctx)
            break
        if _slots_full(ctx):  # the previous start took the last slot; the game says so only now
            nav.click(ctx, atlas.RS_SLOTS_FULL_CLOSE, 800)
            ctx.log("research: slots full")
            break
        ctx.log("research: started")
        started += 1
        _park(ctx)
    nav.big_close(ctx)
