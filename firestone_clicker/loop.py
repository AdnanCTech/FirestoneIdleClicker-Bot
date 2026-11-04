"""Cycle: run each enabled feature, go home between them, pause, repeat."""

from __future__ import annotations

import time
import traceback
from collections.abc import Callable
from pathlib import Path

from firestone_clicker import nav
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx, Stopped
from firestone_clicker.features import alchemist, guardian, guild, heroes, map_missions, research

Feature = Callable[[Ctx, Config], None]
FEATURES: list[tuple[str, Feature]] = [
    ("heroes", heroes.run),
    ("guild", guild.run),
    ("guardian", guardian.run),
    ("alchemist", alchemist.run),
    ("research", research.run),
    ("map_missions", map_missions.run),
]
GUILD_KEYS = ("expeditions", "awaken", "ptree")
MAX_HOME_FAILURES = 3


def enabled(name: str, cfg: Config) -> bool:
    if name == "guild":
        return any(cfg.features.get(k) for k in GUILD_KEYS)
    return bool(cfg.features.get(name))


def _diag(ctx: Ctx, name: str) -> None:
    save = getattr(ctx, "save_png", None)
    if save is None:
        return
    Path("diag").mkdir(exist_ok=True)
    try:
        save(f"diag/{name}-{time.strftime('%Y%m%d-%H%M%S')}.png")
    except Exception as e:  # a failed diagnostic must not mask the feature's error
        ctx.log(f"diag capture failed: {e}")


def run_cycle(ctx: Ctx, cfg: Config, only: str | None = None) -> bool:
    """One pass over the features. Returns False when go_home failed at the end."""
    for name, feature in FEATURES:
        if only is not None and name != only:
            continue
        if only is None and not enabled(name, cfg):
            continue
        ctx.log(f"--- {name}")
        try:
            feature(ctx, cfg)
        except Stopped:
            raise
        except Exception:
            ctx.log(f"{name} failed:\n{traceback.format_exc()}")
            _diag(ctx, name)
        if not nav.go_home(ctx):
            return False
    return nav.go_home(ctx)


def main(ctx: Ctx, cfg: Config, once: str | None, single_cycle: bool = False) -> None:
    failures = 0
    try:
        while True:
            if run_cycle(ctx, cfg, once):
                failures = 0
            else:
                failures += 1
                _diag(ctx, "home")
                if failures >= MAX_HOME_FAILURES:
                    ctx.log(f"exit: go_home failed {MAX_HOME_FAILURES} cycles in a row")
                    return
            if once is not None or single_cycle:
                return
            ctx.log(f"cycle done, sleeping {cfg.delay_s}s")
            ctx.sleep(cfg.delay_s * 1000)
    except Stopped:
        ctx.log("exit: stop requested")
