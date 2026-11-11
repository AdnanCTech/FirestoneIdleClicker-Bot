from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import campaign_loot

CLAIM = (35, 936, 250, 1001)  # the "Next loot" Claim on the Campaign map, live 2026-11-11 (grey then)


def _main():
    s = blank()
    paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    return s


def _battles():
    s = _main()
    paint(s, atlas.ARENA_BATTLES_X.rect, 0xFFF9CE)
    return s


def _campaign(ready):
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.DM_CAMPAIGN_OPEN.rect, 0x0BA108)
    paint(s, CLAIM, 0x0BA108 if ready else 0x7A7A7A)
    paint(s, (100, 960, 185, 978), 0xFFFFFF)
    return s


def test_grey_claim_means_not_ready_and_retries_later():
    c = FakeCtx([_main(), _battles(), _campaign(False)] + [_main()] * 10)
    assert campaign_loot.run(c, Config()) is False
    assert "loot: not ready" in c.logs and not any(936 <= y <= 1001 and x <= 250 for x, y in c.clicks)


def test_green_claim_is_pressed_once_and_counts_as_done():
    c = FakeCtx([_main(), _battles(), _campaign(True)] + [_campaign(False)] * 10)
    assert campaign_loot.run(c, Config()) is True
    assert sum(1 for x, y in c.clicks if 936 <= y <= 1001 and x <= 250) == 1
    assert "loot: claimed" in c.logs


def test_claim_with_a_gem_is_skipped():
    paid = _campaign(True)
    paint(paid, (60, 950, 80, 970), 0xC040E0)
    c = FakeCtx([_main(), _battles(), paid] + [paid] * 10)
    assert campaign_loot.run(c, Config()) is False
    assert not any(936 <= y <= 1001 and x <= 250 for x, y in c.clicks)
