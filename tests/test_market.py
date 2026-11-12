from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import market

FREE = (551, 850, 796, 901)  # green Free of the Mystery box, live 2026-11-12
CHECKIN = (1258, 816, 1430, 857)  # Check In on the calendar tab, live 2026-11-12


def _main():
    return blank()


def _tab1(claimable=True):
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.MARKET_OPEN.rect, 0x7E82EC)
    paint(s, FREE, 0x0A9F06 if claimable else 0x9A9A9A)
    paint(s, (650, 865, 700, 885), 0xFFFFFF)
    return s


def _calendar(claimable=True):
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.MARKET_OPEN.rect, 0x7E82EC)
    paint(s, atlas.MARKET_CHECKIN_OPEN.rect, 0xF2C65A)
    paint(s, CHECKIN, 0x45981F if claimable else 0xBBB9BB)
    paint(s, (1320, 830, 1370, 845), 0xFFFFFF)
    return s


def _free_clicks(c):
    return [p for p in c.clicks if 551 <= p[0] <= 796 and 850 <= p[1] <= 901]


def _checkin_clicks(c):
    return [p for p in c.clicks if 1258 <= p[0] <= 1430 and 816 <= p[1] <= 857]


def test_claims_free_box_and_checks_in():
    # market icon -> tab1, Free -> claimed tab1, calendar tab -> calendar, Check In -> checked
    c = FakeCtx([_main(), _tab1(), _tab1(False), _calendar(), _calendar(False)] + [_main()] * 10)
    assert market.run(c, Config()) is True
    assert (1860, 601) in c.clicks and (1385, 126) in c.clicks
    assert len(_free_clicks(c)) == 1 and len(_checkin_clicks(c)) == 1
    assert "market: free box claimed" in c.logs and "market: checked in" in c.logs


def test_already_claimed_is_left_alone_but_counts_as_done():
    c = FakeCtx([_main(), _tab1(False), _calendar(False)] + [_main()] * 10)
    assert market.run(c, Config()) is True
    assert not _free_clicks(c) and not _checkin_clicks(c)
    assert "market: free box already claimed" in c.logs and "market: already checked in" in c.logs


def test_free_with_a_gem_is_skipped():
    paid = _tab1()
    paint(paid, (600, 870, 620, 890), 0xC040E0)
    c = FakeCtx([_main(), paid, _calendar(False)] + [_calendar(False)] * 10)
    market.run(c, Config())
    assert not _free_clicks(c)


def test_calendar_tab_not_opening_retries_later():
    c = FakeCtx([_main(), _tab1(False), _tab1(False)] + [_tab1(False)] * 10)
    assert market.run(c, Config()) is False
    assert not _checkin_clicks(c)


def test_market_not_opening_retries_later():
    c = FakeCtx([_main(), _main()] + [_main()] * 10)
    assert market.run(c, Config()) is False
    assert not _free_clicks(c)
