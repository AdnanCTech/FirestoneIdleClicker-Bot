"""python -m firestone_clicker [--dry-run] [--once FEATURE] [--settings PATH]"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from firestone_clicker import config, loop, win
from firestone_clicker.ctx import LiveCtx, install_hotkey


def _parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="firestone_clicker")
    p.add_argument("--dry-run", action="store_true", help="run one cycle with clicks and keys disabled")
    p.add_argument("--once", choices=[n for n, _ in loop.FEATURES], help="run a single feature then exit")
    p.add_argument("--settings", type=Path, default=Path("settings.toml"))
    return p.parse_args()


def main() -> int:
    args = _parse()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("bot.log", encoding="utf-8")],
    )
    cfg = config.load(args.settings)
    try:
        ctx = LiveCtx.connect(dry_run=args.dry_run)
    except win.BadWindow as e:
        logging.error("cannot start: %s", e)
        return 2
    install_hotkey(ctx.stop)
    ctx.log(f"connected, client offset {ctx.offset}, dry_run={args.dry_run}. Win+Esc stops.")

    def window_ok() -> bool:
        # The game must be the foreground window: pynput sends to whatever has focus.
        hwnd = win.find_game_window()
        if hwnd is None:
            return False
        if not win.is_foreground(hwnd):
            win.activate(hwnd)
            ctx.sleep(500)
        return win.is_foreground(hwnd)

    ok = loop.main(ctx, cfg, once=args.once, single_cycle=args.dry_run, window_ok=window_ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
