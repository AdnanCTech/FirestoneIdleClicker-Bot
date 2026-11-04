"""Print FOUND/missing for every atlas probe and draw every point/probe on a capture.

Usage: uv run python tools/probe_check.py [out.png]
"""

import sys
from dataclasses import fields, is_dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mss.tools  # noqa: E402
import numpy as np  # noqa: E402

from firestone_clicker import atlas, nav  # noqa: E402
from firestone_clicker.atlas import Point, Probe  # noqa: E402
from firestone_clicker.ctx import LiveCtx  # noqa: E402


def walk(obj, name, out):
    if isinstance(obj, (Point, Probe)):
        out.append((name, obj))
    elif isinstance(obj, (tuple, list)):
        for i, v in enumerate(obj):
            walk(v, f"{name}[{i}]", out)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, f"{name}[{k}]", out)
    elif is_dataclass(obj) and not isinstance(obj, type):
        for f in fields(obj):
            walk(getattr(obj, f.name), f"{name}.{f.name}", out)


items: list[tuple[str, Point | Probe]] = []
for k, v in vars(atlas).items():
    if not k.startswith("_") and k.isupper():
        walk(v, k, items)

ctx = LiveCtx.connect()
img = ctx.grab(nav.CLIENT_RECT).copy()
oy = atlas.REF_ORIGIN[1]
for name, it in items:
    if isinstance(it, Probe):
        hit = nav.found(ctx, it)
        print(f"{'FOUND  ' if hit else 'missing'} {name} {it.rect} #{it.color:06X}")
        x1, y1, x2, y2 = it.rect
        col = (0, 255, 0) if hit else (0, 0, 255)
        img[y1 - oy : y2 - oy + 1, [x1, x2], :3] = col
        img[[y1 - oy, y2 - oy], x1 : x2 + 1, :3] = col
    else:
        x, y = it.x, it.y - oy
        img[max(0, y - 6) : y + 7, x, :3] = (255, 255, 0)
        img[y, max(0, x - 6) : x + 7, :3] = (255, 255, 0)
out = sys.argv[1] if len(sys.argv) > 1 else "diag/probe_check.png"
Path(out).parent.mkdir(exist_ok=True)
mss.tools.to_png(np.ascontiguousarray(img[:, :, [2, 1, 0]]).tobytes(), (img.shape[1], img.shape[0]), output=out)
print("wrote", out)
