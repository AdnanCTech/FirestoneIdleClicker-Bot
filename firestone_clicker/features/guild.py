"""One guild visit: expeditions, awakening and the personal tree."""

from __future__ import annotations

from firestone_clicker import atlas, nav
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx


def expeditions(ctx: Ctx) -> None:
    if not nav.found(ctx, atlas.GUILD_EXPEDITION_DOT):
        return
    nav.click(ctx, atlas.GUILD_EXPEDITIONS, 1500)
    # First click claims the finished expedition, second starts the next one.
    for _ in range(2):
        nav.safe_click(ctx, atlas.GUILD_EXPEDITION_START, atlas.GUILD_EXPEDITION_START_RECT, 1000)
    ctx.sleep(1000)
    nav.big_close(ctx)
    ctx.log("expeditions: claimed and started")
    ctx.sleep(500)
    if nav.found(ctx, atlas.GUILD_EXPEDITION_DOT):
        ctx.sleep(500)
        if nav.found(ctx, atlas.GUILD_EXPEDITION_DOT):
            nav.click(ctx, atlas.GUILD_EXPEDITIONS, 1500)
            nav.safe_click(ctx, atlas.GUILD_EXPEDITION_START, atlas.GUILD_EXPEDITION_START_RECT, 1000)
            nav.big_close(ctx)


def awaken(ctx: Ctx) -> None:
    if not nav.found(ctx, atlas.AWAKEN_DOT):
        return
    nav.click(ctx, atlas.AWAKEN_OPEN, 1500)
    nav.click(ctx, atlas.AWAKEN_X1, 1000)
    if nav.found(ctx, atlas.AWAKEN_BUTTON_ORANGE):
        for probe, button in atlas.AWAKEN_MULTIPLIERS:
            if nav.found(ctx, atlas.AWAKEN_AUTO_READY):
                break
            if nav.found(ctx, probe):
                nav.safe_click(ctx, button, probe.rect, 1000)
        if nav.found(ctx, atlas.AWAKEN_AUTO_READY):
            if nav.safe_click(ctx, atlas.AWAKEN_AUTO, atlas.AWAKEN_AUTO_RECT, 20000):
                ctx.log("awaken: auto")
    elif nav.found(ctx, atlas.AWAKEN_BUTTON_GREEN):
        if nav.safe_click(ctx, atlas.AWAKEN_BUTTON, atlas.AWAKEN_BUTTON_RECT, 3000):
            ctx.log("awaken: single")
    nav.big_close(ctx)


def ptree(ctx: Ctx, cfg: Config) -> None:
    nav.click(ctx, atlas.GUILD_PTREE_ENTRY, 1500)
    nav.click(ctx, atlas.PTREE_OPEN, 1500)
    for key, node in atlas.PTREE_NODES:
        if not cfg.ptree.get(key):
            continue
        nav.click(ctx, node, 1000)
        if not nav.found(ctx, atlas.PTREE_POPUP):
            ctx.log(f"ptree: {key} no popup, skipped")
            continue
        if nav.safe_click(ctx, atlas.PTREE_BUY, atlas.PTREE_BUY_RECT, 1000):
            if nav.found(ctx, atlas.PTREE_NEED_MORE):
                ctx.log("ptree: out of expedition tokens")
                nav.click(ctx, atlas.PTREE_NEED_MORE_CLOSE, 800)
                nav.click(ctx, atlas.PTREE_POPUP_CLOSE, 800)
                break
            ctx.log(f"ptree: bought {key}")
        if nav.found(ctx, atlas.PTREE_POPUP):
            nav.click(ctx, atlas.PTREE_POPUP_CLOSE, 800)
    nav.big_close(ctx)


def run(ctx: Ctx, cfg: Config) -> None:
    f = cfg.features
    if not (f.get("expeditions") or f.get("awaken") or f.get("ptree")):
        return
    if not nav.require_screen(ctx, atlas.MAIN_GUILD_ICON):
        return
    if f.get("expeditions"):
        expeditions(ctx)
    if f.get("awaken"):
        awaken(ctx)
    if f.get("ptree"):
        ptree(ctx, cfg)
    nav.big_close(ctx)
