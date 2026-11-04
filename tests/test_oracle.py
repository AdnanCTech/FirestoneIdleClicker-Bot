from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import oracle


def _oracle():
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    return s


def _button(s, i, color=0x0AA008):
    x1, y1, x2, y2 = atlas.ORACLE_RITUAL_BUTTONS[i]
    paint(s, (x1 + 70, y1 + 8, x2 - 70, y2 - 8), color)


def _in(clicks, rect):
    x1, y1, x2, y2 = rect
    return any(x1 <= x <= x2 and y1 <= y <= y2 for x, y in clicks)


def test_opens_rituals_tab_and_clicks_every_green_button():
    s = _oracle()
    _button(s, 1)
    _button(s, 3)
    c = FakeCtx([s] * 12)
    oracle.run(c, Config())
    assert (1023, 994) in c.clicks and (828, 436) in c.clicks
    assert _in(c.clicks, atlas.ORACLE_RITUAL_BUTTONS[1]) and _in(c.clicks, atlas.ORACLE_RITUAL_BUTTONS[3])
    assert not _in(c.clicks, atlas.ORACLE_RITUAL_BUTTONS[0])
    assert c.clicks[-1] == (1851, 84)


def test_gem_priced_button_is_skipped():
    s = _oracle()
    _button(s, 0)
    paint(s, (1160, 500, 1180, 520), 0xC040E0)
    c = FakeCtx([s] * 12)
    oracle.run(c, Config())
    assert not _in(c.clicks, atlas.ORACLE_RITUAL_BUTTONS[0])


def test_reward_popup_okay_is_pressed():
    s = _oracle()
    _button(s, 0)
    popup = _oracle()
    paint(popup, (805, 598, 1114, 668), 0x0AA008)
    # town, oracle, tab, claim -> popup
    c = FakeCtx([s, s, s, popup] + [_oracle()] * 8)
    oracle.run(c, Config())
    assert _in(c.clicks, (805, 598, 1114, 668))


def test_nothing_green_just_closes():
    c = FakeCtx([_oracle()] * 8)
    oracle.run(c, Config())
    assert c.clicks == [(1023, 994), (828, 436), (1851, 84)]
