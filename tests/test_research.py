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


def _tree_box(s, x1, y1):
    """An available box as drawn in the game: blue with a white title and a yellow bar."""
    paint(s, (x1, y1, x1 + 383, y1 + 101), 0x0848D8)
    paint(s, (x1 + 120, y1 + 20, x1 + 340, y1 + 45), 0xF8F8F8)
    paint(s, (x1 + 100, y1 + 70, x1 + 360, y1 + 88), 0xEFCF23)  # bar rows measured live 2026-11-06
    paint(s, (x1 + 10, y1 + 15, x1 + 90, y1 + 90), 0xF06060)


def test_available_box_with_text_and_bar_is_found():
    s = _library()
    _tree_box(s, 225, 471)
    boxes = research.available_boxes(FakeCtx([s]))
    assert len(boxes) == 1
    x1, y1, x2, y2 = boxes[0]
    assert abs(x1 - 225) <= 8 and abs(y1 - 471) <= 8 and x2 - x1 > 300 and y2 - y1 > 80


def test_claims_both_slots_after_layout_shift():
    # Two finished slots. After the first claim the game re-lays out the strip and the
    # second button moves: a list captured before clicking would miss it.
    both = _library()
    paint(both, (533, 917, 691, 975), 0x0AA008)
    paint(both, (1180, 917, 1338, 975), 0x16BC15)
    shifted = _library()
    paint(shifted, (533, 917, 691, 975), 0x0AA008)  # the remaining one slid left
    # town, library, tree tab, claim #1 -> shifted, claim #2 -> empty
    c = FakeCtx([both, both, both, shifted, _library(), _library()])
    research.run(c, Config())
    claims = [p for p in c.clicks if 917 <= p[1] <= 975]
    assert len(claims) == 2 and all(533 <= x <= 691 for x, _ in claims)


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


def _bar(s, x1, y1, fill):
    """Progress bar as measured live 2026-11-06: dark track 0x172874, yellow fill 0xEFCF23."""
    paint(s, (x1 + 100, y1 + 70, x1 + 360, y1 + 88), 0x172874)
    if fill:
        paint(s, (x1 + 100, y1 + 70, x1 + 100 + int(260 * fill), y1 + 88), 0xEFCF23)


def test_picks_rightmost_column_then_lowest_bar():
    # Live 2026-11-06, Tree XII: column 2 had health 15/60, damage 0/60, armor 0/60 and the
    # bot started health every time because it was the first blob. Columns unlock on levels
    # in the previous column, so the rightmost open column gets the starts, lowest bar first.
    s = _library()
    _tree_box(s, 225, 224)
    _bar(s, 225, 224, 0.0)  # column 1, empty, but a column behind
    _tree_box(s, 680, 222)
    _bar(s, 680, 222, 0.25)
    _tree_box(s, 680, 470)
    _bar(s, 680, 470, 0.0)
    _tree_box(s, 680, 710)
    _bar(s, 680, 710, 0.0)
    box = research.pick_box(FakeCtx([s]))
    assert abs(box[0] - 680) <= 8 and abs(box[1] - 470) <= 8, box
    popup = s.copy()
    paint(popup, (650, 680, 942, 740), 0x0AA008)
    c = FakeCtx([s, s, popup] + [_library()] * 10)
    research.run(c, Config())
    assert _in_band(c.clicks, 680, 470, 1063, 571) and not _in_band(c.clicks, 680, 222, 1063, 323)
