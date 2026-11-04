from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import alchemist


def _alchemist():
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    return s


def test_classify():
    other = blank()[0:70, 0:185].copy()
    free = other.copy()
    paint(free, (0, 0, 184, 69), 0xF9AA47)
    paid = free.copy()
    paint(paid, (80, 20, 100, 40), 0xC040E0)
    assert alchemist.classify(other) == "other"
    assert alchemist.classify(free) == "free"
    assert alchemist.classify(paid) == "paid"


def test_collects_done_and_starts_idle():
    s = _alchemist()
    blood, dust, coin = atlas.ALCHEMY_SLOTS
    paint(s, blood.complete.rect, 0x0AA008)  # blood done -> collect
    # dust: nothing painted -> "other", not running -> start
    paint(s, coin.in_progress.rect, 0x916A38)  # coin running -> leave
    c = FakeCtx([s] * 12)
    alchemist.run(c, Config())
    assert (949, 777) in c.clicks and (1286, 786) in c.clicks and (1641, 767) not in c.clicks


def test_never_clicks_paid():
    s = _alchemist()
    blood = atlas.ALCHEMY_SLOTS[0]
    paint(s, blood.button, 0xF9AA47)
    paint(s, (900, 780, 930, 800), 0xC040E0)
    c = FakeCtx([s] * 12)
    alchemist.run(c, Config())
    assert (949, 777) not in c.clicks and (951, 771) not in c.clicks


def test_grey_unaffordable_start_is_skipped():
    s = _alchemist()
    coin = atlas.ALCHEMY_SLOTS[2]
    paint(s, coin.not_running.rect, 0xFFC700)
    paint(s, coin.button, 0x8A8A8A)
    c = FakeCtx([s] * 12)
    alchemist.run(c, Config())
    assert (1641, 767) not in c.clicks


def test_disabled_slot_not_started():
    s = _alchemist()
    cfg = Config()
    cfg.alchemist["strange_dust"] = False
    c = FakeCtx([s] * 12)
    alchemist.run(c, cfg)
    assert (1286, 786) not in c.clicks
