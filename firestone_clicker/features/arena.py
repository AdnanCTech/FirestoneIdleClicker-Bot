"""Arena of Kings: fight the configured opponent position until the daily attempts run out.

Every attempt is used in one visit. The bot cannot read the "N/5" counter, so it stops when
pressing Fight no longer opens the battle window (and saves a capture of what it sees).
"""

from __future__ import annotations

from firestone_clicker import atlas, nav, vision
from firestone_clicker.atlas import Point
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx

Rect = tuple[int, int, int, int]


def _centre(r: Rect) -> Point:
    return Point((r[0] + r[2]) // 2, (r[1] + r[3]) // 2)


def fight_buttons(ctx: Ctx) -> list[Rect]:
    band = atlas.ARENA_FIGHT_BAND
    return vision.green_boxes(ctx.grab(band), (band[0], band[1]), min_w=atlas.ARENA_FIGHT_MIN_W)


def _wait_ok(ctx: Ctx) -> Rect | None:
    band = atlas.ARENA_OK_BAND
    waited = 0
    while waited <= atlas.ARENA_FIGHT_MAX_MS:
        boxes = vision.green_boxes(ctx.grab(band), (band[0], band[1]), min_w=atlas.ARENA_FIGHT_MIN_W)
        if boxes:
            return boxes[0]
        ctx.sleep(atlas.ARENA_POLL_MS)
        waited += atlas.ARENA_POLL_MS
    return None


def _diag(ctx: Ctx, name: str) -> None:
    save = getattr(ctx, "save_png", None)
    if save is not None:
        save(f"diag/{name}.png")


def _close(ctx: Ctx) -> None:
    x = nav.find_dialog_x(ctx, atlas.ARENA_POPUP_X_BAND)
    if x is not None:
        nav.click(ctx, x, 800)
    nav.click(ctx, atlas.ARENA_CLOSE, 800)
    nav.big_close(ctx, 800)


def _fight(ctx: Ctx, button: Rect) -> bool:
    """One attempt: Fight, the red button, wait for the result, OK. False when the pass must stop."""
    nav.click(ctx, _centre(button), 1000)
    if not nav.wait_for(ctx, atlas.ARENA_BATTLE_BUTTON, atlas.ARENA_OPEN_MS):
        ctx.log("arena: battle window did not open, done for today")  # e.g. the 1000-token offer
        _diag(ctx, "arena_no_battle")
        return False
    if not nav.safe_click(ctx, atlas.ARENA_BATTLE, atlas.ARENA_BATTLE_RECT, 1000):
        return False
    ok = _wait_ok(ctx)
    if ok is None:
        ctx.log("arena: fight did not end")
        _diag(ctx, "arena_stuck")
        return False
    ctx.log("arena: won")
    return nav.safe_click(ctx, _centre(ok), ok, 1500)


def run(ctx: Ctx, cfg: Config) -> None:
    if not nav.require_screen(ctx, atlas.ARENA_BATTLES, atlas.ARENA_BATTLES_X, via_town=True):
        return
    nav.click(ctx, atlas.ARENA_CARD, 1000)
    if not nav.wait_for(ctx, atlas.ARENA_OPEN):
        ctx.log("arena: did not open")
        return
    fights = 0
    while fights < atlas.ARENA_MAX_FIGHTS:
        if not nav.found(ctx, atlas.ARENA_HAS_ATTEMPTS):
            ctx.log("arena: no attempts left")
            break
        buttons = fight_buttons(ctx)
        if len(buttons) < cfg.arena_opponent:
            ctx.log(f"arena: {len(buttons)} Fight button(s), wanted position {cfg.arena_opponent}")
            break
        if not _fight(ctx, buttons[cfg.arena_opponent - 1]):
            break
        fights += 1
    ctx.log(f"arena: {fights} fight(s)")
    _close(ctx)
