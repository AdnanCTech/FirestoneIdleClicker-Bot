"""World map: claim finished missions from the left panel, start available ones (free only).

The map is never dragged or zoomed. Available missions are found by their teal icon ring;
a popup is acted on only through a wide green button that shows no gem, so an in-progress
popup (orange "Complete instantly" with a gem price) is just closed.
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


def available_icons(ctx: Ctx) -> list[tuple[int, int]]:
    """Centres of mission icons, found by colour; nearby hits (one icon, two colours) merge."""
    area = atlas.MAP_ICON_AREA
    img = ctx.grab(area)
    out: list[tuple[int, int]] = []
    for color, var, min_px in atlas.MAP_ICON_COLORS:
        for box in vision.blobs(img, (area[0], area[1]), color, var, min_px, cell=4):
            p = _centre(box)
            if all(abs(p.x - x) > atlas.MAP_ICON_MERGE or abs(p.y - y) > atlas.MAP_ICON_MERGE for x, y in out):
                out.append((p.x, p.y))
    return out


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
