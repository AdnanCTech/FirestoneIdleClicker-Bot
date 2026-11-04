"""`--check`: list every atlas probe, test it on the live screen, draw the result."""

from __future__ import annotations

from dataclasses import fields, is_dataclass

import numpy as np

from firestone_clicker import atlas, nav
from firestone_clicker.atlas import Point, Probe
from firestone_clicker.ctx import Ctx

MAIN_SCREEN = ("MM_SETTINGS_OPEN", "DIALOG_CLOSE_X", "TOWN_OPEN")


def _walk(obj, name: str, out: list) -> None:
    if isinstance(obj, (Point, Probe)):
        out.append((name, obj))
    elif isinstance(obj, (tuple, list)):
        for i, v in enumerate(obj):
            _walk(v, f"{name}[{i}]", out)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _walk(v, f"{name}[{k}]", out)
    elif is_dataclass(obj) and not isinstance(obj, type):
        for f in fields(obj):
            _walk(getattr(obj, f.name), f"{name}.{f.name}", out)


def atlas_items() -> list[tuple[str, Point | Probe]]:
    out: list = []
    for k, v in vars(atlas).items():
        if not k.startswith("_") and k.isupper():
            _walk(v, k, out)
    return out


def atlas_probes() -> list[tuple[str, Probe]]:
    return [(n, p) for n, p in atlas_items() if isinstance(p, Probe)]


def report(ctx: Ctx, probes: list[tuple[str, Probe]]) -> list[str]:
    return [f"{'FOUND  ' if nav.found(ctx, p) else 'missing'} {n}" for n, p in probes]


def annotate(ctx: Ctx, img: np.ndarray) -> np.ndarray:
    """Draw every probe rect (green found / red missing) and point (yellow cross) on a client capture."""
    img = img.copy()
    oy = atlas.REF_ORIGIN[1]
    for _, it in atlas_items():
        if isinstance(it, Probe):
            x1, y1, x2, y2 = it.rect
            col = (0, 255, 0) if nav.found(ctx, it) else (0, 0, 255)
            img[y1 - oy : y2 - oy + 1, [x1, x2], :3] = col
            img[[y1 - oy, y2 - oy], x1 : x2 + 1, :3] = col
        else:
            x, y = it.x, it.y - oy
            img[max(0, y - 6) : y + 7, x, :3] = (255, 255, 0)
            img[y, max(0, x - 6) : x + 7, :3] = (255, 255, 0)
    return img
