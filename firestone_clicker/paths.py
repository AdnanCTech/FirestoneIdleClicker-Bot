"""Where settings, log and diagnostics live: next to the exe when frozen, else the cwd."""

from __future__ import annotations

import sys
from pathlib import Path

DEFAULT_SETTINGS = """\
# Pause between cycles in seconds. A full cycle with everything on takes a minute or two.
delay_s = 60

# Which automations run each cycle.
[features]
expeditions = true
awaken = true
ptree = false
map_missions = true
alchemist = true
research = true
heroes = true
guardian = true
oracle = true
arena = true

# Which alchemist experiments to start.
[alchemist]
dragon_blood = true
strange_dust = true
exotic_coins = true

# Which slots in the heroes menu (U key) to upgrade when their button is green.
[heroes]
h1 = true
h2 = true
h3 = true
h4 = true
h5 = true
guardian = true
special = true

# Magic Quarter: evolve when the red dot shows, train guardian number train_target (1 to 4).
[guardian]
evolve = true
train = true
train_target = 1

# Arena of Kings: which opponent to fight, 1 (strongest) to 3 (weakest), every attempt each day.
[arena]
opponent = 3

# Personal tree nodes to buy (only when features.ptree is true).
[ptree]
AttDmg = true
AttHp = true
AttArm = true
Energy = true
Mana = true
Rage = true
Miner = true
Battle = true
MainAtt = true
Prest = true
Fire = true
Gold = true
Level = true
Guard = true
Fist = true
Prec = true
Magic = true
Tank = true
Damage = true
Heal = true
"""


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def base_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def ensure_settings(path: Path) -> bool:
    """Write the default settings file if none exists. True when it was created."""
    if path.exists():
        return False
    path.write_text(DEFAULT_SETTINGS, encoding="utf-8")
    return True
