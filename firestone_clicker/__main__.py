"""FirestoneClicker [--dry-run] [--once FEATURE] [--check] [--settings PATH] [--version]"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from firestone_clicker import __version__, check, config, loop, paths, win
from firestone_clicker.ctx import LiveCtx, install_hotkey


def _parse(base: Path) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="FirestoneClicker")
    p.add_argument("--dry-run", action="store_true", help="run one cycle with clicks and keys disabled")
    p.add_argument("--once", choices=[n for n, _ in loop.FEATURES], help="run a single feature then exit")
    p.add_argument("--check", action="store_true", help="report the game window and main-screen markers, then exit")
    p.add_argument("--settings", type=Path, default=base / "settings.toml")
    p.add_argument("--version", action="version", version=f"FirestoneClicker {__version__}")
    return p.parse_args()


def _pause_if_frozen() -> None:
    # A double-clicked exe closes its console on exit; keep the message readable.
    if paths.is_frozen():
        try:
            input("Press Enter to close")
        except EOFError:
            pass


def _run_check(ctx: LiveCtx, base: Path) -> int:
    import mss.tools
    import numpy as np

    from firestone_clicker import nav

    print(f"game window found, client 1920x1009 at screen x={ctx.offset[0]}, y={ctx.offset[1] + 31}")
    (base / "diag").mkdir(exist_ok=True)
    out = base / "diag" / "check.png"
    img = check.annotate(ctx, ctx.grab(nav.CLIENT_RECT))
    mss.tools.to_png(np.ascontiguousarray(img[:, :, [2, 1, 0]]).tobytes(), (img.shape[1], img.shape[0]), output=str(out))
    print(f"capture with every probe drawn: {out}")
    # The one navigation the bot depends on: the gear opens settings, settings closes again.
    ok = nav.go_home(ctx)
    print(
        "navigation OK: settings opened and closed, you are on the main screen"
        if ok
        else "navigation FAILED: could not open and close settings. Close any dialog, use the classic layout, and retry."
    )
    return 0 if ok else 1


atlas_origin = (0, 31)


def main() -> int:
    base = paths.base_dir()
    args = _parse(base)
    if paths.ensure_settings(args.settings):
        print(f"created default {args.settings}")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(base / "bot.log", encoding="utf-8")],
    )
    try:
        cfg = config.load(args.settings)
    except ValueError as e:
        print(f"settings.toml problem: {e}")
        _pause_if_frozen()
        return 2
    try:
        ctx = LiveCtx.connect(dry_run=args.dry_run)
    except win.BadWindow as e:
        msg = str(e)
        if "not found" in msg:
            print("Firestone is not running. Start the game, reach the main screen, then run this again.")
        else:
            print(f"Game window is the wrong size: {msg}")
            print("Needs a 1920x1080 monitor at 100% display scaling with the game windowed.")
        _pause_if_frozen()
        return 2
    if args.check:
        code = _run_check(ctx, base)
        _pause_if_frozen()
        return code
    install_hotkey(ctx.stop)
    ctx.log(f"FirestoneClicker {__version__} connected, client offset {ctx.offset}, dry_run={args.dry_run}. Win+Esc or Ctrl+C stops.")

    def window_ok() -> bool:
        # The game must be the foreground window: pynput sends to whatever has focus.
        hwnd = win.find_game_window()
        if hwnd is None:
            return False
        if not win.is_foreground(hwnd):
            win.activate(hwnd)
            ctx.sleep(500)
        return win.is_foreground(hwnd)

    import os

    os.chdir(base)  # diag/ captures from loop.py land next to the exe
    ok = loop.main(ctx, cfg, once=args.once, single_cycle=args.dry_run, window_ok=window_ok)
    if not ok:
        _pause_if_frozen()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
