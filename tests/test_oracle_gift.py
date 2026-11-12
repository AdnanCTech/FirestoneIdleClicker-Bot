from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import oracle_gift

FREE = (571, 771, 817, 821)  # green Free of the Oracle's gift, live 2026-11-12


def _main():
    s = blank()
    paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    return s


def _oracle():
    s = _main()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    return s


def _market(claimable=True):
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.ORACLE_MARKET_OPEN.rect, 0x23354A)
    paint(s, FREE, 0x0B9F07 if claimable else 0x9A9A9A)
    paint(s, (670, 785, 720, 805), 0xFFFFFF)
    return s


def _free_clicks(c):
    return [p for p in c.clicks if 571 <= p[0] <= 817 and 771 <= p[1] <= 821]


def test_claims_the_gift():
    # town opens by key (no screen advance); oracle -> oracle, market tab -> market, Free -> claimed
    c = FakeCtx([_main(), _oracle(), _market(), _market(False)] + [_oracle()] * 10)
    assert oracle_gift.run(c, Config()) is True
    assert (1023, 994) in c.clicks and (828, 771) in c.clicks
    assert len(_free_clicks(c)) == 1 and "oracle gift: claimed" in c.logs


def test_already_claimed_counts_as_done():
    c = FakeCtx([_main(), _oracle(), _market(False)] + [_oracle()] * 10)
    assert oracle_gift.run(c, Config()) is True
    assert not _free_clicks(c) and "oracle gift: already claimed" in c.logs


def test_free_with_a_gem_is_skipped():
    paid = _market()
    paint(paid, (600, 790, 620, 810), 0xC040E0)
    c = FakeCtx([_main(), _oracle(), paid] + [paid] * 10)
    oracle_gift.run(c, Config())
    assert not _free_clicks(c)


def test_market_tab_not_opening_retries_later():
    c = FakeCtx([_main(), _oracle(), _oracle()] + [_oracle()] * 10)
    assert oracle_gift.run(c, Config()) is False
    assert not _free_clicks(c)
