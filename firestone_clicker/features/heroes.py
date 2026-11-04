"""Hero upgrades in the classic U menu: one click per slot whose button is green."""

from __future__ import annotations

from firestone_clicker import atlas, nav, vision
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx


def run(ctx: Ctx, cfg: Config) -> None:
    ctx.key("u")
    ctx.sleep(1500)
    for key, rect, point in atlas.HERO_UPGRADE_SLOTS:
        if not cfg.heroes.get(key):
            continue
        if vision.any_match(ctx.grab(rect), atlas.GREEN_BUTTON, 3):
            gem_rect = (point.x - 100, point.y - 25, point.x + 100, point.y + 25)
            if nav.safe_click(ctx, point, gem_rect, 600):
                ctx.log(f"heroes: upgraded {key}")
    nav.big_close(ctx)
