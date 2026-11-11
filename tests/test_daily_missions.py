from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import daily_missions

DUNGEON_FIGHTS = ((634, 736, 893, 801), (1026, 736, 1285, 801))  # live 2026-11-11
OK = (833, 718, 1086, 780)


def _main():
    s = blank()
    paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    return s


def _battles():
    s = _main()
    paint(s, atlas.ARENA_BATTLES_X.rect, 0xFFF9CE)
    return s


def _campaign():
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.DM_CAMPAIGN_OPEN.rect, 0x0BA108)
    return s


def _daily():
    s = _campaign()
    paint(s, atlas.DM_DAILY_X.rect, 0xFFF9CE)
    return s


def _window(*buttons):
    s = blank()
    paint(s, atlas.DM_WINDOW_X.rect, 0xFFF9CE)
    for b in buttons:
        paint(s, b, 0x0BA108)
        x1, y1, x2, y2 = b
        paint(s, ((x1 + x2) // 2 - 40, (y1 + y2) // 2 - 8, (x1 + x2) // 2 + 40, (y1 + y2) // 2 + 8), 0xFFFFFF)
    return s


def _ok():
    s = blank()
    paint(s, OK, 0x0BA108)
    return s


def _lib(*xs, art=0x3060A0):
    s = _window(*((x, 736, x + 259, 801) for x in xs))
    paint(s, (140, 230, 1795, 500), art)  # card pictures: the drag detector looks here
    return s


def test_clears_both_dungeons_then_every_liberation_card_with_scrolling():
    l1 = _lib(200)
    l2 = _lib(art=0x3060A0)  # liberated, same view
    l3 = _lib(600, art=0x80A030)  # after a drag: a new card in view
    l4 = _lib(art=0x80A030)
    screens = [
        _main(), _battles(), _campaign(), _daily(),
        _window(*DUNGEON_FIGHTS), _ok(), _window(DUNGEON_FIGHTS[1]), _ok(), _window(), _daily(),
        l1, l1,  # Liberation opens; the drag to the start changes nothing
        _ok(), l2,  # first card fought
        l3,  # drag forward reveals another
        _ok(), l4,  # fought
        l4,  # drag forward: unchanged, the end
        _daily(), _campaign(), _main(),
    ] + [_main()] * 5
    c = FakeCtx(screens)
    assert daily_missions.run(c, Config()) is True
    assert c.clicks.count((959, 749)) == 4  # the OK after each of the 4 fights
    assert c.logs.count("daily: dungeon won") == 2 and c.logs.count("daily: liberation won") == 2
    assert c.drags[0] == (500, 381, 1500, 381) and (1500, 381, 500, 381) in c.drags
    assert "daily: 2 liberation(s)" in c.logs and (1763, 95) in c.clicks and (1475, 119) in c.clicks


def test_fight_that_never_ends_gives_up_without_marking_done():
    running = blank()
    c = FakeCtx([_main(), _battles(), _campaign(), _daily(), _window(*DUNGEON_FIGHTS)] + [running] * 10)
    assert daily_missions.run(c, Config()) is False
    assert "daily: dungeon fight did not end" in c.logs


def test_fight_button_with_a_gem_is_not_pressed():
    paid = _window(*DUNGEON_FIGHTS)
    paint(paid, (750, 760, 770, 780), 0xC040E0)
    c = FakeCtx([_main(), _battles(), _campaign(), _daily(), paid] + [paid] * 10)
    assert daily_missions.run(c, Config()) is False
    assert not any(abs(y - 768) <= 6 and 600 <= x <= 900 for x, y in c.clicks)  # the Fight centre; "Open" sits at y 799


def test_button_cut_off_by_the_window_edge_is_not_a_target():
    s = _window((1700, 736, 1795, 801))  # the next card's Liberate, mostly off screen
    assert daily_missions.fight_buttons(FakeCtx([s])) == []
