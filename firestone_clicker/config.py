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


def _merge(target: dict[str, bool], src: dict, section: str) -> None:
    for k, v in src.items():
        if k not in target:
            raise ValueError(f"unknown key [{section}] {k}")
        target[k] = bool(v)


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
    return cfg
