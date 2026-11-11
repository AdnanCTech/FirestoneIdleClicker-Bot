from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import pickaxes

CLAIM = (590, 721, 838, 776)  # green Claim of the free pickaxe card, live 2026-11-11


def _guild():
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    return s


def _market():
    s = _guild()
    paint(s, atlas.PICK_MARKET_OPEN.rect, 0xBFB095)
    return s


def _supplies(claimable=True):
    s = _market()
    paint(s, atlas.PICK_SUPPLIES_OPEN.rect, 0x433018)
    if claimable:
        paint(s, CLAIM, 0x0BA108)
        paint(s, (690, 740, 740, 758), 0xFFFFFF)
    else:
        paint(s, CLAIM, 0x616365)
    return s


def test_claims_free_pickaxes_from_the_supplies_tab():
    # guild icon -> guild, market -> market, supplies -> supplies, claim -> claimed
    c = FakeCtx([blank(), _guild(), _market(), _supplies(), _supplies(False)] + [_guild()] * 10)
    assert pickaxes.run(c, Config()) is True
    assert (630, 365) in c.clicks and (115, 752) in c.clicks
    assert any(590 <= x <= 838 and 721 <= y <= 776 for x, y in c.clicks)
    assert "pickaxes: claimed" in c.logs


def test_already_claimed_card_is_left_alone_but_counts_as_done():
    c = FakeCtx([blank(), _guild(), _market(), _supplies(False)] + [_guild()] * 10)
    assert pickaxes.run(c, Config()) is True
    assert not any(590 <= x <= 838 and 721 <= y <= 776 for x, y in c.clicks)
    assert "pickaxes: nothing to claim" in c.logs


def test_claim_with_a_gem_is_skipped():
    paid = _supplies()
    paint(paid, (700, 735, 720, 755), 0xC040E0)
    c = FakeCtx([blank(), _guild(), _market(), paid] + [paid] * 10)
    pickaxes.run(c, Config())
    assert not any(590 <= x <= 838 and 721 <= y <= 776 for x, y in c.clicks)


def test_supplies_tab_not_reached_retries_later():
    c = FakeCtx([blank(), _guild(), _market()] + [_market()] * 10)
    assert pickaxes.run(c, Config()) is False
    assert not any(590 <= x <= 838 and 721 <= y <= 776 for x, y in c.clicks)
