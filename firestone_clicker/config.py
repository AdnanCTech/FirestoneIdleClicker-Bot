from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

FEATURE_KEYS = (
    "expeditions",
    "awaken",
    "ptree",
    "map_missions",
    "alchemist",
    "research",
    "heroes",
    "guardian",
    "oracle",
    "arena",
    "pickaxes",
    "daily_missions",
    "campaign_loot",
    "engineer",
    "market",
)
ALCHEMIST_KEYS = ("dragon_blood", "strange_dust", "exotic_coins")
HERO_KEYS = ("h1", "h2", "h3", "h4", "h5", "guardian", "special")
PTREE_KEYS = (
    "AttDmg", "AttHp", "AttArm", "Energy", "Mana", "Rage", "Miner", "Battle", "MainAtt", "Prest",
    "Fire", "Gold", "Level", "Guard", "Fist", "Prec", "Magic", "Tank", "Damage", "Heal",
)


def _all_on(keys: tuple[str, ...]) -> dict[str, bool]:
    return {k: True for k in keys}


@dataclass
class Config:
    delay_s: int = 60
    features: dict[str, bool] = field(default_factory=lambda: _all_on(FEATURE_KEYS))
    alchemist: dict[str, bool] = field(default_factory=lambda: _all_on(ALCHEMIST_KEYS))
    heroes: dict[str, bool] = field(default_factory=lambda: _all_on(HERO_KEYS))
    guardian_evolve: bool = True
    guardian_train: bool = True
    guardian_train_target: int = 1
    ptree: dict[str, bool] = field(default_factory=lambda: _all_on(PTREE_KEYS))
    arena_opponent: int = 3
    arena_run_at: list[int] = field(default_factory=lambda: [1, 13])
    pickaxes_run_at: list[int] = field(default_factory=lambda: [1, 13])
    daily_missions_run_at: list[int] = field(default_factory=lambda: [1, 13])
    campaign_loot_run_at: list[int] = field(default_factory=lambda: [1, 7, 13, 19])
    engineer_run_at: list[int] = field(default_factory=lambda: [1, 7, 13, 19])
    market_run_at: list[int] = field(default_factory=lambda: [1, 13])


def _merge(target: dict[str, bool], src: dict, section: str) -> None:
    for k, v in src.items():
        if k not in target:
            raise ValueError(f"unknown key [{section}] {k}")
        target[k] = bool(v)


def _hours(data: dict, section: str, default: list[int]) -> list[int]:
    hours = [int(h) for h in data.get(section, {}).get("run_at", default)]
    if not hours or any(not 0 <= h <= 23 for h in hours):
        raise ValueError(f"{section}.run_at must list hours 0 to 23")
    return hours


def load(path: Path) -> Config:
    cfg = Config()
    if not path.exists():
        return cfg
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    cfg.delay_s = int(data.get("delay_s", cfg.delay_s))
    _merge(cfg.features, data.get("features", {}), "features")
    _merge(cfg.alchemist, data.get("alchemist", {}), "alchemist")
    _merge(cfg.heroes, data.get("heroes", {}), "heroes")
    _merge(cfg.ptree, data.get("ptree", {}), "ptree")
    g = data.get("guardian", {})
    cfg.guardian_evolve = bool(g.get("evolve", cfg.guardian_evolve))
    cfg.guardian_train = bool(g.get("train", cfg.guardian_train))
    cfg.guardian_train_target = int(g.get("train_target", cfg.guardian_train_target))
    if not 1 <= cfg.guardian_train_target <= 4:
        raise ValueError("guardian.train_target must be 1 to 4")
    cfg.arena_opponent = int(data.get("arena", {}).get("opponent", cfg.arena_opponent))
    if not 1 <= cfg.arena_opponent <= 3:
        raise ValueError("arena.opponent must be 1 to 3")
    cfg.arena_run_at = _hours(data, "arena", cfg.arena_run_at)
    cfg.pickaxes_run_at = _hours(data, "pickaxes", cfg.pickaxes_run_at)
    cfg.daily_missions_run_at = _hours(data, "daily_missions", cfg.daily_missions_run_at)
    cfg.campaign_loot_run_at = _hours(data, "campaign_loot", cfg.campaign_loot_run_at)
    cfg.engineer_run_at = _hours(data, "engineer", cfg.engineer_run_at)
    cfg.market_run_at = _hours(data, "market", cfg.market_run_at)
    return cfg
