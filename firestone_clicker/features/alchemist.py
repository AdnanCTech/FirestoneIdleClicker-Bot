"""Alchemist: collect finished experiments, complete free speed-ups, start idle slots.

A start click never lands on an orange button: a running experiment's "Speed up" sits at the
same spot and may be a gem purchase.
"""

from __future__ import annotations

from typing import Literal

import numpy as np

from firestone_clicker import atlas, nav, vision
from firestone_clicker.atlas import AlchemySlot
from firestone_clicker.config import Config
from firestone_clicker.ctx import Ctx

Look = Literal["other", "free", "paid"]
CONFIRM_MS = 150
GREY_MIN = 0.3  # measured live: grey start button 0.42, orange buttons ~0


def classify(img: np.ndarray) -> Look:
    if vision.color_share(img, atlas.ORANGE_1, 40) < atlas.ALCHEMY_BUTTON_ORANGE_MIN:
        return "other"
    return "paid" if vision.gem_share(img) > atlas.ALCHEMY_GEM_MAX else "free"


def _look(ctx: Ctx, slot: AlchemySlot) -> Look:
    ctx.move(atlas.ALCHEMY_PARK.x, atlas.ALCHEMY_PARK.y)
    ctx.sleep(CONFIRM_MS)
    return classify(ctx.grab(slot.button))


def _free_twice(ctx: Ctx, slot: AlchemySlot) -> bool:
    return _look(ctx, slot) == "free" and _look(ctx, slot) == "free"


def run(ctx: Ctx, cfg: Config) -> None:
    wanted = [s for s in atlas.ALCHEMY_SLOTS if cfg.alchemist.get(s.key)]
    if not wanted:
        return
    if not nav.require_screen(ctx, atlas.TOWN_ALCHEMIST, via_town=True):
        return
    ctx.move(atlas.ALCHEMY_PARK.x, atlas.ALCHEMY_PARK.y)
    ctx.sleep(500)
    for slot in wanted:
        if nav.found(ctx, slot.not_running):
            continue
        if nav.found(ctx, slot.complete):
            nav.click(ctx, slot.collect, 1000)
            ctx.log(f"alchemist: collected {slot.key}")
    for slot in wanted:
        if _free_twice(ctx, slot):
            nav.click(ctx, slot.collect, 1000)
            ctx.log(f"alchemist: completed free {slot.key}")
    for slot in wanted:
        look = _look(ctx, slot)
        if look == "paid":
            continue
        if look == "free":
            if _free_twice(ctx, slot):
                nav.click(ctx, slot.collect, 1000)
            continue
        if nav.found(ctx, slot.in_progress):
            continue
        if _look(ctx, slot) != "other":
            continue
        if vision.grey_share(ctx.grab(slot.button)) > GREY_MIN:
            ctx.log(f"alchemist: {slot.key} unaffordable, skipped")
            continue
        nav.click(ctx, slot.start, 1000)
        ctx.log(f"alchemist: started {slot.key}")
    nav.big_close(ctx)
