"""World map: claim finished missions from the left panel, start available ones (free only).

The map is never dragged or zoomed. Every icon is opened (found by the pin stand under it);
a popup is acted on only through a wide green button that shows no gem, so an in-progress
popup (orange "Speed up" with a gem price) or one short of squads is just closed.
"""

from __future__ import annotations

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
    for kind, color, var, min_px in atlas.MAP_ICON_KINDS:
        if patch.size and int(vision.match_mask(patch, color, var).sum()) >= min_px:
            return kind
    return "other"


def available_icons(ctx: Ctx) -> list[tuple[int, int]]:
    """Click points of every mission icon (found by the beige pin stand under each one),
    preferred kinds first in MAP_PRIORITY order, then the rest top to bottom."""
    area = atlas.MAP_ICON_AREA
    color, var, min_px = atlas.MAP_ICON_STAND
    img = ctx.grab(area)
    found: list[tuple[int, int, int]] = []
    for x1, y1, x2, _ in vision.blobs(img, (area[0], area[1]), color, var, min_px, cell=4):
        x, y = (x1 + x2) // 2, y1 - atlas.MAP_ICON_ABOVE_STAND
        if all(abs(x - ox) > atlas.MAP_ICON_MERGE or abs(y - oy) > atlas.MAP_ICON_MERGE for _, ox, oy in found):
            kind = _kind(img, x - area[0], y1 - area[1])
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


def _start_pass(ctx: Ctx) -> None:
    icons = available_icons(ctx)
    ctx.log(f"map: {len(icons)} icon(s) found")
    started = closed = 0
    for x, y in icons:
        if started >= atlas.MAP_MAX_STARTS:
            break
        if not nav.found(ctx, atlas.MAP_IDLE_BANNER):
            ctx.log("map: no more idle squads")
            break
        nav.click(ctx, Point(x, y), 1200)
        if _press_green_or_close(ctx, f"started mission at {x},{y}"):
            started += 1
        else:
            closed += 1
    ctx.log(f"map: {started} started, {closed} popups closed (in progress or not startable)")
    ctx.move(atlas.MAP_POPUP_OUTSIDE.x, atlas.MAP_POPUP_OUTSIDE.y)


def run(ctx: Ctx, cfg: Config) -> None:
    ctx.key("m")
    if not nav.wait_for(ctx, atlas.DIALOG_CLOSE_X):
        ctx.log("map did not open")
        return
    ctx.sleep(1000)
    ctx.move(atlas.MAP_POPUP_OUTSIDE.x, atlas.MAP_POPUP_OUTSIDE.y)
    _free_refresh(ctx)
    _collect(ctx)
    if nav.found(ctx, atlas.MAP_IDLE_BANNER):
        _start_pass(ctx)
    else:
        ctx.log("map: no idle squads, start pass skipped")
    nav.go_home(ctx)
