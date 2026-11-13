"""World map: claim finished missions from the left panel, start available ones (free only).

The map is never dragged or zoomed. Every icon is opened (found by the pin stand under it);
a popup is acted on only through a wide green button that shows no gem, so an in-progress
popup (orange "Speed up" with a gem price) or one short of squads is just closed.
"""

from __future__ import annotations

import time

import numpy as np

from firestone_clicker import atlas, nav, vision
from firestone_clicker.atlas import Point
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx

Rect = tuple[int, int, int, int]


def _centre(r: Rect) -> Point:
    return Point((r[0] + r[2]) // 2, (r[1] + r[3]) // 2)


def _green_button(ctx: Ctx) -> Rect | None:
    band = atlas.MAP_POPUP_BAND
    boxes = vision.green_boxes(ctx.grab(band), (band[0], band[1]))
    return boxes[0] if boxes else None


def _close_popup(ctx: Ctx) -> None:
    x = nav.find_dialog_x(ctx, atlas.MAP_POPUP_X_BAND)
    nav.click(ctx, x or atlas.MAP_POPUP_OUTSIDE, 800)


def _press_green_or_close(ctx: Ctx, label: str) -> bool:
    button = _green_button(ctx)
    if button is not None and nav.safe_click(ctx, _centre(button), button, 1500):
        ctx.log(f"map: {label}")
        return True
    _close_popup(ctx)
    return False


def _kind(img, x: int, stand_top: int) -> str:
    """Mission kind from the disc colours above the stand; "other" when no key matches."""
    half, above, below = atlas.MAP_ICON_SAMPLE
    patch = img[max(0, stand_top - above) : max(0, stand_top - below), max(0, x - half) : x + half]
    for kind, keys in atlas.MAP_ICON_KINDS:
        if patch.size and all(int(vision.match_mask(patch, color, var).sum()) >= min_px for color, var, min_px in keys):
            return kind
    return "other"


def idle_banner(ctx: Ctx) -> bool:
    """The "Your squads are idling" banner is showing (enough brown text pixels in its band)."""
    p = atlas.MAP_IDLE_BANNER
    return int(vision.match_mask(ctx.grab(p.rect), p.color, p.var).sum()) >= atlas.MAP_IDLE_BANNER_MIN_PX


def _banner_rows(img, area: Rect) -> int:
    """How many rows at the bottom of the capture the idle banner covers (0 when it is lower)."""
    x = atlas.MAP_BANNER_COLUMN - area[0]
    col = vision.match_mask(img[:, x : x + 1], *atlas.MAP_BANNER_FACE)[:, 0]
    n = 0
    while n < len(col) and col[len(col) - 1 - n]:
        n += 1
    return n


def available_icons(ctx: Ctx) -> list[tuple[int, int]]:
    """Click points of every mission icon (found by the beige pin stand under each one),
    preferred kinds first in MAP_PRIORITY order, then the rest top to bottom."""
    area = atlas.MAP_ICON_AREA
    color, var, min_px = atlas.MAP_ICON_STAND
    img = ctx.grab(area)
    img = img[: len(img) - _banner_rows(img, area)]  # the banner's gradient matches the stand colour
    mask = vision.match_mask(img, color, var)
    min_w, min_total = atlas.MAP_ICON_STAND_SHAPE
    found: list[tuple[int, int, int]] = []
    for x1, y1, x2, y2 in vision.blobs(img, (area[0], area[1]), color, var, min_px, cell=4):
        # The cell grid trims the stand's tail, so measure the real pixels around the blob.
        sy, sx = max(0, y1 - area[1] - 4), max(0, x1 - area[0] - 4)
        sub = mask[sy : y2 - area[1] + 5, sx : x2 - area[0] + 5]
        rows = sub.sum(axis=1)
        if int(rows.sum()) < min_total or int(rows.max()) < min_w:
            continue
        top = area[1] + sy + int(rows.argmax())  # widest row is the stand's top edge
        x, y = (x1 + x2) // 2, top - atlas.MAP_ICON_ABOVE_STAND
        if all(abs(x - ox) > atlas.MAP_ICON_MERGE or abs(y - oy) > atlas.MAP_ICON_MERGE for _, ox, oy in found):
            kind = _kind(img, x - area[0], top - area[1])
            rank = atlas.MAP_PRIORITY.index(kind) if kind in atlas.MAP_PRIORITY else len(atlas.MAP_PRIORITY)
            found.append((rank, x, y))
    found.sort(key=lambda f: f[0])  # stable: within a rank the blob order (top to bottom) holds
    return [(x, y) for _, x, y in found]


def _free_refresh(ctx: Ctx) -> None:
    if nav.found(ctx, atlas.MR_FREE_RESET) and vision.gem_share(ctx.grab(atlas.MR_REFRESH_RECT)) <= nav.GEM_MAX:
        nav.click(ctx, atlas.MR_FREE_RESET_BUTTON, 1500)
        ctx.log("map: free refresh")


def _collect(ctx: Ctx) -> None:
    claimed = 0
    for _ in range(atlas.MAP_MAX_COLLECT):
        if nav.found(ctx, atlas.MR_NO_MISSIONS) or not nav.found(ctx, atlas.MR_MISSION_DONE):
            break
        nav.click(ctx, atlas.MR_FIRST_MISSION, 1200)
        if _press_green_or_close(ctx, "claimed"):
            claimed += 1
    ctx.log(f"map: {claimed} claimed" if claimed else "map: nothing to claim")


def _start_pass(ctx: Ctx) -> int:
    icons = available_icons(ctx)
    ctx.log(f"map: {len(icons)} icon(s) found")
    started = closed = 0
    for x, y in icons:
        if started >= atlas.MAP_MAX_STARTS:
            break
        if not idle_banner(ctx):
            ctx.log("map: no more idle squads")
            break
        nav.click(ctx, Point(x, y), 1200)
        if _press_green_or_close(ctx, f"started mission at {x},{y}"):
            started += 1
        else:
            closed += 1
    ctx.log(f"map: {started} started, {closed} popups closed (in progress or not startable)")
    ctx.move(atlas.MAP_POPUP_OUTSIDE.x, atlas.MAP_POPUP_OUTSIDE.y)
    return started


def _changed(before: np.ndarray, after: np.ndarray) -> bool:
    diff = np.abs(before[:, :, :3].astype(np.int16) - after[:, :, :3].astype(np.int16)).max(axis=2) > 40
    return float(diff.mean()) > atlas.MAP_VIEW_CHANGE


def _pan(ctx: Ctx, direction: str, icons: list[tuple[int, int]], vector: tuple[int, int] | None = None) -> bool:
    """Drag the map one screen (or `vector`) to reveal what lies in `direction`; False at the edge."""
    dx, dy = vector or atlas.MAP_PAN[direction]
    clear = atlas.MAP_PAN_CLEAR
    starts = atlas.MAP_PAN_STARTS[direction]
    x, y = next((p for p in starts if all(abs(p[0] - ix) > clear or abs(p[1] - iy) > clear for ix, iy in icons)), starts[0])
    before = ctx.grab(atlas.MAP_ICON_AREA)
    ctx.drag(x, y, x + dx, y + dy)
    ctx.move(atlas.MAP_POPUP_OUTSIDE.x, atlas.MAP_POPUP_OUTSIDE.y)
    ctx.sleep(700)  # the pan glides to a stop
    return _changed(before, ctx.grab(atlas.MAP_ICON_AREA))


def _pan_to_edge(ctx: Ctx, direction: str) -> None:
    for _ in range(atlas.MAP_PAN_MAX):
        if not _pan(ctx, direction, available_icons(ctx)):
            return


def _home_view(ctx: Ctx) -> None:
    """Put the view back on the continent: top-left corner, then a fixed drag left and up."""
    _pan_to_edge(ctx, "up")
    _pan_to_edge(ctx, "left")
    dx, dy = atlas.MAP_HOME_DRAG
    _pan(ctx, "right", available_icons(ctx), (-dx, 0))
    _pan(ctx, "down", available_icons(ctx), (0, -dy))


_next_sweep = 0.0  # monotonic time before which a sweep is pointless (the last one found nothing)


def _sweep_views(ctx: Ctx) -> int:
    """Walk the whole map from its top-left corner, one screen at a time, starting what it finds."""
    _pan_to_edge(ctx, "up")
    _pan_to_edge(ctx, "left")
    started = 0
    for _ in range(atlas.MAP_PAN_MAX + 1):
        for _ in range(atlas.MAP_PAN_MAX + 1):
            started += _start_pass(ctx)
            if not idle_banner(ctx):
                return started
            if not _pan(ctx, "right", available_icons(ctx)):
                break
        if not _pan(ctx, "down", available_icons(ctx)):
            break
        _pan_to_edge(ctx, "left")
    return started


def _sweep(ctx: Ctx) -> None:
    global _next_sweep
    if time.monotonic() < _next_sweep:
        ctx.log("map: sweep skipped, last one found nothing")
        return
    ctx.log("map: squads still idle, sweeping the map")
    started = _sweep_views(ctx)
    _home_view(ctx)
    if not started:
        ctx.log("map: sweep found nothing")
        _next_sweep = time.monotonic() + atlas.MAP_SWEEP_COOLDOWN_S


def run(ctx: Ctx, cfg: Config) -> None:
    ctx.key("m")
    if not nav.wait_for(ctx, atlas.DIALOG_CLOSE_X):
        ctx.log("map did not open")
        return
    ctx.sleep(1000)
    ctx.move(atlas.MAP_POPUP_OUTSIDE.x, atlas.MAP_POPUP_OUTSIDE.y)
    _free_refresh(ctx)
    _collect(ctx)
    if idle_banner(ctx):
        _start_pass(ctx)
        if idle_banner(ctx):
            _sweep(ctx)
    else:
        ctx.log("map: no idle squads, start pass skipped")
    nav.go_home(ctx)
