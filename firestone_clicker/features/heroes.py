"""Hero upgrades in the classic U menu: one click per slot whose button is green."""

from __future__ import annotations

from firestone_clicker import atlas, nav, vision
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx


def run(ctx: Ctx, cfg: Config) -> None:
    ctx.key("u")
    ctx.sleep(1500)
    upgraded, not_ready, off = [], [], []
    for key, rect, point in atlas.HERO_UPGRADE_SLOTS:
        if not cfg.heroes.get(key):
            off.append(key)
            continue
        if vision.any_match(ctx.grab(rect), atlas.GREEN_BUTTON, 3):
            gem_rect = (point.x - 100, point.y - 25, point.x + 100, point.y + 25)
            if nav.safe_click(ctx, point, gem_rect, 600):
                ctx.log(f"heroes: upgraded {key}")
                upgraded.append(key)
        else:
            not_ready.append(key)
    ctx.log(
        f"heroes: {len(upgraded)} upgraded, {len(not_ready)} not green"
        + (f" ({', '.join(not_ready)})" if not_ready else "")
        + (f", {len(off)} off" if off else "")
    )
    nav.big_close(ctx)
