from conftest import blank, paint

from firestone_clicker import atlas, nav
from firestone_clicker.ctx import FakeCtx


def test_go_home_detects_settings_and_closes():
    s0 = blank()
    s1 = blank()
    paint(s1, atlas.MM_SETTINGS_OPEN.rect, 0x285483)
    c = FakeCtx([s0, s1])
    assert nav.go_home(c) is True
    assert c.clicks == [(1851, 84), (1725, 116)]


def test_go_home_gives_up():
    c = FakeCtx([blank()])
    assert nav.go_home(c) is False
    assert len(c.clicks) <= 10


def test_safe_click_skips_gem():
    s = blank()
    paint(s, (100, 100, 200, 150), 0x0AA008)
    paint(s, (150, 110, 170, 130), 0xC040E0)
    c = FakeCtx([s])
    assert nav.safe_click(c, atlas.Point(150, 125), (100, 100, 200, 150)) is False
    assert c.clicks == []


def test_safe_click_clicks_when_clean():
    s = blank()
    paint(s, (100, 100, 200, 150), 0x0AA008)
    c = FakeCtx([s])
    assert nav.safe_click(c, atlas.Point(150, 125), (100, 100, 200, 150)) is True
    assert c.clicks == [(150, 125)]


def test_wait_for_needs_two_hits():
    s = blank()
    paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    assert nav.wait_for(FakeCtx([s]), atlas.TOWN_OPEN) is True
    assert nav.wait_for(FakeCtx([blank()]), atlas.TOWN_OPEN, timeout_ms=300) is False
