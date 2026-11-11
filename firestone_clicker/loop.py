"""Cycle: run each enabled feature, go home between them, pause, repeat."""

from __future__ import annotations

import time
import traceback
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from firestone_clicker import nav, schedule
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx, Stopped
from firestone_clicker.features import alchemist, arena, daily_missions, guardian, guild, heroes, map_missions, oracle, pickaxes, research

Feature = Callable[[Ctx, Config], None]
FEATURES: list[tuple[str, Feature]] = [
    ("heroes", heroes.run),
    ("guild", guild.run),
    ("guardian", guardian.run),
    ("alchemist", alchemist.run),
    ("oracle", oracle.run),
    ("research", research.run),
    ("map_missions", map_missions.run),
    ("arena", arena.run),
    ("pickaxes", pickaxes.run),
    ("daily_missions", daily_missions.run),
]
GUILD_KEYS = ("expeditions", "awaken", "ptree")
# Features that run once per window (hours from the config); the feature returns True when done.
SCHEDULED: dict[str, Callable[[Config], list[int]]] = {
    "arena": lambda cfg: cfg.arena_run_at,
    "pickaxes": lambda cfg: cfg.pickaxes_run_at,
    "daily_missions": lambda cfg: cfg.daily_missions_run_at,
}
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


def run_cycle(
    ctx: Ctx,
    cfg: Config,
    only: str | None = None,
    state: schedule.State | None = None,
    now: Callable[[], datetime] = datetime.now,
) -> bool:
    """One pass over the features. Returns False when go_home failed at the end."""
    for name, feature in FEATURES:
        if only is not None and name != only:
            continue
        if only is None and not enabled(name, cfg):
            continue
        win = schedule.window(SCHEDULED[name](cfg), now()) if name in SCHEDULED and only is None else None
        if win is not None and state is not None and state.done(name, win):
            continue
        ctx.log(f"--- {name}")
        t0 = time.monotonic()
        try:
            if feature(ctx, cfg) is True and win is not None and state is not None:
                state.mark(name, win)
        except Stopped:
            raise
        except Exception:
            ctx.log(f"{name} failed:\n{traceback.format_exc()}")
            _diag(ctx, name)
        home = nav.go_home(ctx)
        ctx.log(f"--- {name} done in {time.monotonic() - t0:.0f}s, back on main: {home}")
        if not home:
            return False
    return nav.go_home(ctx)


def main(
    ctx: Ctx,
    cfg: Config,
    once: str | None,
    single_cycle: bool = False,
    window_ok: Callable[[], bool] = lambda: True,
    state: schedule.State | None = None,
) -> bool:
    """Run cycles until stopped. False means the bot gave up (window lost or stuck)."""
    failures = 0
    try:
        while True:
            if not window_ok():
                ctx.log("exit: game window gone or not in front")
                return False
            if run_cycle(ctx, cfg, once, state):
                failures = 0
            else:
                failures += 1
                _diag(ctx, "home")
                if failures >= MAX_HOME_FAILURES:
                    ctx.log(f"exit: go_home failed {MAX_HOME_FAILURES} cycles in a row")
                    return False
            if once is not None or single_cycle:
                return True
            ctx.log(f"cycle done, sleeping {cfg.delay_s}s")
            ctx.sleep(cfg.delay_s * 1000)
    except Stopped:
        ctx.log("exit: stop requested")
        return True
    except KeyboardInterrupt:
        ctx.log("exit: Ctrl+C")
        return True
