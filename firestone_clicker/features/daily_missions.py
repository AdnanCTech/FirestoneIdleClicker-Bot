"""Daily missions (town > Battles > Campaign > Daily missions): clear both Dungeon fights and
every Liberation card, once per schedule window.

A fight starts straight from its green button, runs on its own and ends with a "Here are your
rewards!" popup whose green OK leads back to the window the fight came from. The Liberation
strip scrolls by dragging and keeps its position, so it is dragged to its start first, then
forward one screen at a time until the view stops changing.
"""

from __future__ import annotations

import numpy as np

from firestone_clicker import atlas, nav, vision
from firestone_clicker.atlas import Point
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx

Rect = tuple[int, int, int, int]


def _centre(r: Rect) -> Point:
    return Point((r[0] + r[2]) // 2, (r[1] + r[3]) // 2)


def _diag(ctx: Ctx, name: str) -> None:
    save = getattr(ctx, "save_png", None)
    if save is not None:
        save(f"diag/{name}.png")


def fight_buttons(ctx: Ctx) -> list[Rect]:
    """Green Fight/Liberate buttons in view, left to right; one cut by the window edge is too narrow."""
    band = atlas.DM_FIGHT_BAND
    return vision.green_boxes(ctx.grab(band), (band[0], band[1]), min_w=atlas.DM_FIGHT_MIN_W)


def _fight(ctx: Ctx, button: Rect, label: str) -> bool:
    if not nav.found(ctx, atlas.DM_WINDOW_X):  # the Daily popup's "Open" buttons look like fights too
        ctx.log(f"daily: {label} window is gone")
        return False
    if not nav.safe_click(ctx, _centre(button), button, 1000):
        return False
    ok = nav.wait_green(ctx, atlas.ARENA_OK_BAND, atlas.ARENA_FIGHT_MIN_W, atlas.ARENA_FIGHT_MAX_MS, atlas.ARENA_POLL_MS)
    if ok is None:
        ctx.log(f"daily: {label} fight did not end")
        _diag(ctx, "daily_stuck")
        return False
    ctx.log(f"daily: {label} won")
    return nav.safe_click(ctx, _centre(ok), ok, 1500)


def _dungeon(ctx: Ctx) -> bool:
    if not nav.require_screen(ctx, atlas.DM_DUNGEON, atlas.DM_WINDOW_X):
        return False
    for _ in range(atlas.DM_DUNGEON_FIGHTS):
        buttons = fight_buttons(ctx)
        if not buttons:
            break
        if not _fight(ctx, buttons[0], "dungeon"):
            return False
    ctx.log("daily: dungeons cleared")
    nav.click(ctx, atlas.DM_WINDOW_CLOSE, 1000)
    return True


def _strip(ctx: Ctx) -> np.ndarray:
    return ctx.grab(atlas.DM_STRIP_AREA)


def _drag(ctx: Ctx, to_start: bool) -> np.ndarray:
    a, b = atlas.DM_DRAG_X
    if to_start:
        ctx.drag(b, atlas.DM_DRAG_Y, a, atlas.DM_DRAG_Y)
    else:
        ctx.drag(a, atlas.DM_DRAG_Y, b, atlas.DM_DRAG_Y)
    ctx.move(atlas.RS_PARK.x, atlas.RS_PARK.y)
    ctx.sleep(800)
    return _strip(ctx)


def _changed(before: np.ndarray, after: np.ndarray) -> bool:
    diff = np.abs(before[:, :, :3].astype(np.int16) - after[:, :, :3].astype(np.int16)).max(axis=2) > 40
    return float(diff.mean()) > atlas.DM_VIEW_CHANGE


def _liberation(ctx: Ctx) -> bool:
    if not nav.require_screen(ctx, atlas.DM_LIBERATION, atlas.DM_WINDOW_X):
        return False
    view = _strip(ctx)
    for _ in range(atlas.DM_MAX_DRAGS):  # the strip remembers its position: start from the left
        after = _drag(ctx, to_start=True)
        if not _changed(view, after):
            break
        view = after
    fights = drags = 0
    while fights < atlas.DM_MAX_FIGHTS:
        buttons = fight_buttons(ctx)
        if buttons:
            if not _fight(ctx, buttons[0], "liberation"):
                return False
            fights += 1
            continue
        if drags >= atlas.DM_MAX_DRAGS:
            break
        before = _strip(ctx)
        drags += 1
        if not _changed(before, _drag(ctx, to_start=False)):
            break
    ctx.log(f"daily: {fights} liberation(s)")
    nav.click(ctx, atlas.DM_WINDOW_CLOSE, 1000)
    return True


def run(ctx: Ctx, cfg: Config) -> bool:
    """True when both windows were worked through; False to retry next cycle."""
    if not nav.require_screen(ctx, atlas.ARENA_BATTLES, atlas.ARENA_BATTLES_X, via_town=True):
        return False
    if not nav.require_screen(ctx, atlas.DM_CAMPAIGN, atlas.DM_CAMPAIGN_OPEN):
        return False
    if not nav.require_screen(ctx, atlas.DM_DAILY, atlas.DM_DAILY_X):
        return False
    done = _dungeon(ctx)
    done = _liberation(ctx) and done
    nav.click(ctx, atlas.DM_DAILY_CLOSE, 800)
    nav.big_close(ctx, 800)
    return done
