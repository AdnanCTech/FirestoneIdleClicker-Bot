"""Find the game window, report geometry, save a capture, park the pointer on the settings gear."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mss.tools  # noqa: E402

from firestone_clicker import atlas, win  # noqa: E402
from firestone_clicker.ctx import LiveCtx  # noqa: E402

hwnd = win.find_game_window()
if hwnd is None:
    sys.exit("Firestone.exe window not found")
win.activate(hwnd)
rect = win.maximize(hwnd)
print("client =", rect)
ctx = LiveCtx()
ctx.attach(rect)
print("offset =", ctx.offset)
ctx.sleep(500)
img = ctx.grab((0, atlas.REF_ORIGIN[1], 1919, atlas.REF_ORIGIN[1] + atlas.REF_SIZE[1] - 1))
Path("diag").mkdir(exist_ok=True)
mss.tools.to_png(img[:, :, [2, 1, 0]].tobytes(), (img.shape[1], img.shape[0]), output="diag/smoke.png")
print("wrote diag/smoke.png", img.shape)
ctx.move(1851, 84)
print("pointer parked on (1851, 84)")
