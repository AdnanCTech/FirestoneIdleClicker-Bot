"""Print FOUND/missing for every atlas probe and draw every point/probe on a capture.

Usage: uv run python tools/probe_check.py [out.png]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mss.tools  # noqa: E402
import numpy as np  # noqa: E402

from firestone_clicker import check, nav  # noqa: E402
from firestone_clicker.ctx import LiveCtx  # noqa: E402

ctx = LiveCtx.connect()
print("\n".join(check.report(ctx, check.atlas_probes())))
img = check.annotate(ctx, ctx.grab(nav.CLIENT_RECT))
out = sys.argv[1] if len(sys.argv) > 1 else "diag/probe_check.png"
Path(out).parent.mkdir(exist_ok=True)
mss.tools.to_png(np.ascontiguousarray(img[:, :, [2, 1, 0]]).tobytes(), (img.shape[1], img.shape[0]), output=out)
print("wrote", out)
