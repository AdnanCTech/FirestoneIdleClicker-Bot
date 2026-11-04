"""Magic Quarter: evolve a guardian when the red dot shows, train the configured guardian."""

from __future__ import annotations

from firestone_clicker import atlas, nav
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx


def run(ctx: Ctx, cfg: Config) -> None:
    if not (cfg.guardian_evolve or cfg.guardian_train):
        return
    if not nav.require_screen(ctx, atlas.TOWN_MAGIC_QUARTER, via_town=True):
        return
    ctx.sleep(1000)
    if cfg.guardian_evolve and nav.found(ctx, atlas.GUARDIAN_EVOLVE_DOT):
        nav.click(ctx, atlas.GUARDIAN_EVOLVE_TAB, 1000)
        if nav.safe_click(ctx, atlas.GUARDIAN_EVOLVE_BUTTON, atlas.GUARDIAN_EVOLVE_RECT, 10500):
            ctx.log("guardian: evolved")
        nav.click(ctx, atlas.GUARDIAN_BACK_TAB, 1000)
    if cfg.guardian_train and nav.found(ctx, atlas.GUARDIAN_TRAIN_READY):
        ctx.key_hold("left", 2000)  # lands on guardian 1
        ctx.sleep(500)
        for _ in range(cfg.guardian_train_target - 1):
            ctx.key("right")
            ctx.sleep(200)
        if nav.safe_click(ctx, atlas.GUARDIAN_TRAIN_BUTTON, atlas.GUARDIAN_TRAIN_RECT, 1000):
            ctx.log(f"guardian: trained #{cfg.guardian_train_target}")
    nav.big_close(ctx)
