from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import research


def _library():
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    return s


def _in_band(clicks, x1, y1, x2, y2):
    return any(x1 <= x <= x2 and y1 <= y <= y2 for x, y in clicks)


def test_claims_done_slot():
    s = _library()
    paint(s, (600, 930, 760, 990), 0x0AA008)  # done button in left slot
    c = FakeCtx([s] * 10)
    research.run(c, Config())
    assert _in_band(c.clicks, 600, 930, 760, 990)


def test_claim_with_gem_is_skipped():
    s = _library()
    paint(s, (600, 930, 760, 990), 0x0AA008)
    paint(s, (670, 950, 690, 970), 0xC040E0)
    c = FakeCtx([s] * 10)
    research.run(c, Config())
    assert not _in_band(c.clicks, 600, 930, 760, 990)


def test_starts_available_box_free_only():
    s = _library()
    paint(s, (225, 224, 608, 325), 0x0D49DE)  # available box
    popup = s.copy()
    paint(popup, (650, 680, 942, 740), 0x0AA008)  # green Research button
    paid = popup.copy()
    paint(paid, (700, 700, 720, 720), 0xC040E0)
    # town, library, tree tab, box click -> popup
    c = FakeCtx([s, s, s, popup, popup, popup, popup])
    research.run(c, Config())
    assert _in_band(c.clicks, 650, 680, 942, 740)
    c2 = FakeCtx([s, s, s, paid, paid, paid, paid])
    research.run(c2, Config())
    assert not _in_band(c2.clicks, 650, 680, 942, 740)


def test_slots_full_closed():
    s = _library()
    paint(s, atlas.RS_SLOTS_FULL_X.rect, 0xFF6109)
    paint(s, atlas.RS_SLOTS_FULL_CREAM.rect, 0xE8D1B7)
    c = FakeCtx([s] * 10)
    research.run(c, Config())
    assert (1370, 355) in c.clicks


def test_no_box_no_click_in_tree():
    c = FakeCtx([_library()] * 10)
    research.run(c, Config())
    assert c.clicks == [(329, 657), (1816, 610), (1851, 84)]
