from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import arena

FIGHT_X = (698, 960, 1221)  # Fight button centres, left (strongest) to right (weakest), live 2026-11-11


def _town():
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    return s


def _battles():
    s = _town()
    paint(s, atlas.ARENA_BATTLES_X.rect, 0xFFF9CE)
    return s


def _opponents():
    s = blank()
    paint(s, atlas.ARENA_OPEN.rect, 0x0D87FF)
    paint(s, atlas.ARENA_HAS_ATTEMPTS.rect, 0xDCC0A5)
    for x in FIGHT_X:
        paint(s, (x - 90, 623, x + 90, 663), 0x0AA008)
        paint(s, (x - 20, 636, x + 20, 650), 0xFFFFFF)
    return s


def _battle():
    s = blank()
    paint(s, (880, 502, 1040, 662), 0xD34429)
    paint(s, (930, 552, 990, 612), 0x731408)
    return s


def _won():
    s = blank()
    paint(s, (833, 753, 1086, 816), 0x0AA008)
    return s


def _cfg(opponent=3):
    cfg = Config()
    cfg.arena_opponent = opponent
    return cfg


def test_fights_configured_opponent_until_the_battle_window_stops_opening():
    # Each fight: Fight -> battle window, red button -> won popup, OK -> opponents.
    # After the last attempt Fight opens nothing (what the game shows at 0/5 is unseen yet).
    fight = [_battle(), _won(), _opponents()]
    stuck = _opponents()
    c = FakeCtx([_town(), _battles(), _opponents()] + fight * 2 + [stuck] * 10)
    arena.run(c, _cfg(3))
    assert c.clicks.count((1221, 643)) == 3 and (960, 582) in c.clicks
    assert c.logs.count("arena: won") == 2 and "arena: battle window did not open, done for today" in c.logs
    assert (698, 643) not in c.clicks and (960, 643) not in c.clicks


def test_opponent_position_is_configurable():
    c = FakeCtx([_town(), _battles(), _opponents()] + [_battle(), _won(), _opponents()] + [_opponents()] * 10)
    arena.run(c, _cfg(1))
    assert (698, 643) in c.clicks and (1221, 643) not in c.clicks


def test_never_more_than_five_fights_per_visit():
    c = FakeCtx([_town(), _battles(), _opponents()] + [_battle(), _won(), _opponents()] * 8)
    arena.run(c, _cfg(3))
    assert c.clicks.count((960, 582)) == 5


def test_fight_that_never_ends_is_abandoned():
    running = blank()
    c = FakeCtx([_town(), _battles(), _opponents(), _battle()] + [running] * 10)
    arena.run(c, _cfg(3))
    assert "arena: fight did not end" in c.logs and c.clicks.count((960, 582)) == 1


def test_red_button_with_a_gem_is_not_pressed():
    paid = _battle()
    paint(paid, (950, 520, 970, 540), 0xC040E0)
    c = FakeCtx([_town(), _battles(), _opponents(), paid] + [paid] * 10)
    arena.run(c, _cfg(3))
    assert (960, 582) not in c.clicks


def test_arena_not_open_gives_up():
    c = FakeCtx([_town(), _battles()] + [_town()] * 10)
    arena.run(c, _cfg(3))
    assert "arena: did not open" in c.logs and not any(y == 643 for _, y in c.clicks)


def test_green_plus_at_zero_attempts_means_no_fight():
    # Live 2026-11-11: at 0/5 a green "+" replaces the cream panel next to the counter and
    # Fight opens a "5 tokens for 1000" offer instead of the battle window.
    s = _opponents()
    paint(s, atlas.ARENA_HAS_ATTEMPTS.rect, 0x5CB31A)
    c = FakeCtx([_town(), _battles(), s] + [s] * 10)
    arena.run(c, _cfg(3))
    assert "arena: no attempts left" in c.logs and (1221, 643) not in c.clicks
