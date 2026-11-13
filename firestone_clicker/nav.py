"""Shared navigation: probes, clicks, gem-gated clicks, go home."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from firestone_clicker import atlas, vision
from firestone_clicker.atlas import Point, Probe
from firestone_clicker.ctx import Ctx

Rect = tuple[int, int, int, int]

GEM_MAX = 0.004
HOVER_MS = 150
CLIENT_RECT = (0, atlas.REF_ORIGIN[1], 1919, atlas.REF_ORIGIN[1] + atlas.REF_SIZE[1] - 1)
THUMB = (32, 18)
STALL_CELLS = 0.30
STALL_DIFF = 40
MAX_STALLS = 3
MAX_CLOSES = 10


def found(ctx: Ctx, probe: Probe) -> bool:
    return vision.any_match(ctx.grab(probe.rect), probe.color, probe.var)


def wait_for(ctx: Ctx, probe: Probe, timeout_ms: float = 6000) -> bool:
    """True once the probe is seen twice 100 ms apart."""
    waited = 0.0
    hits = 0
    while waited <= timeout_ms:
        hits = hits + 1 if found(ctx, probe) else 0
        if hits >= 2:
            return True
        ctx.sleep(100)
        waited += 100
    return False


def click(ctx: Ctx, p: Point, settle_ms: float = 1500) -> None:
    ctx.move(p.x, p.y)
    ctx.sleep(HOVER_MS)
    ctx.click(p.x, p.y)
    ctx.sleep(settle_ms)


def safe_click(ctx: Ctx, p: Point, rect: Rect, settle_ms: float = 1500) -> bool:
    """Click unless the button rect shows a gem icon."""
    share = vision.gem_share(ctx.grab(rect))
    if share > GEM_MAX:
        ctx.log(f"gem: skipped {p.x},{p.y} (share {share:.4f})")
        return False
    click(ctx, p, settle_ms)
    return True


def big_close(ctx: Ctx, settle_ms: float = 1500) -> None:
    click(ctx, atlas.BIG_CLOSE, settle_ms)


def open_town(ctx: Ctx) -> bool:
    ctx.key("t")
    return wait_for(ctx, atlas.TOWN_OPEN)


def require_screen(ctx: Ctx, p: Point, expect: Probe = atlas.DIALOG_CLOSE_X, via_town: bool = False) -> bool:
    if via_town and not open_town(ctx):
        ctx.log("town did not open")
        return False
    click(ctx, p, 1000)
    ok = wait_for(ctx, expect)
    if not ok:
        ctx.log(f"screen at {p.x},{p.y} did not open")
    return ok


def wait_green(ctx: Ctx, band: Rect, min_w: int, timeout_ms: int, poll_ms: int) -> Rect | None:
    """First wide green button to appear in `band` within the timeout (a fight's result popup)."""
    waited = 0
    while waited <= timeout_ms:
        boxes = vision.green_boxes(ctx.grab(band), (band[0], band[1]), min_w=min_w)
        if boxes:
            return boxes[0]
        ctx.sleep(poll_ms)
        waited += poll_ms
    return None


def find_dialog_x(ctx: Ctx, band: Rect, min_ring: int = 40) -> Point | None:
    """Centre of an orange-ring X (cream cross inside) within `band`, or None."""
    img = ctx.grab(band)
    rings = vision.color_boxes(img, (band[0], band[1]), atlas.DIALOG_RING, 30, min_ring, min_ring, fill=0.2)
    for x1, y1, x2, y2 in rings:
        inner = ctx.grab((x1, y1, x2, y2))
        if vision.any_match(inner, atlas.DIALOG_X_CROSS, 30):
            return Point((x1 + x2) // 2, (y1 + y2) // 2)
    return None


def thumbnail(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    tw, th = THUMB
    cells = img[: (h // th) * th, : (w // tw) * tw, :3].astype(np.float32)
    return cells.reshape(th, h // th, tw, w // tw, 3).mean(axis=(1, 3, 4))


def changed(a: np.ndarray, b: np.ndarray) -> bool:
    return bool((np.abs(a - b) >= STALL_DIFF).mean() >= STALL_CELLS)


def capture(ctx: Ctx, name: str) -> None:
    """Save the screen as diag/<name>.png when the context can (a failed capture only logs)."""
    save = getattr(ctx, "save_png", None)
    if save is None:
        return
    Path("diag").mkdir(exist_ok=True)
    try:
        save(f"diag/{name}.png")
    except Exception as e:  # a failed diagnostic must not mask the feature's error
        ctx.log(f"diag capture failed: {e}")


def go_home(ctx: Ctx) -> bool:
    """Click the big X until the settings window appears (proof of the main screen), then close it."""
    stalls = 0
    for _ in range(MAX_CLOSES):
        if found(ctx, atlas.MM_SETTINGS_OPEN):
            click(ctx, atlas.SETTINGS_CLOSE, 800)
            return True
        before = thumbnail(ctx.grab(CLIENT_RECT))
        # Only the big X: a ring search over the whole screen matches orange map art.
        click(ctx, atlas.BIG_CLOSE, 800)
        if not changed(before, thumbnail(ctx.grab(CLIENT_RECT))):
            stalls += 1
            if stalls >= MAX_STALLS:
                break
    ctx.log("go_home: gave up")
    return False
