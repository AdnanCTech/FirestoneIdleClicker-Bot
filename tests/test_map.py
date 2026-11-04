from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import map_missions


def _map():
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.MR_NO_MISSIONS.rect, 0x1452B4)
    return s


def _icon(s, x, y):
    paint(s, (x - 25, y - 25, x + 25, y + 25), 0xF07070)


def test_icons_of_each_colour_and_merge():
    s = _map()
    _icon(s, 600, 400)
    paint(s, (900 - 8, 400 - 8, 900 + 8, 400 + 8), 0x00A8B0)  # scroll ring patch
    paint(s, (1200 - 8, 400 - 8, 1200 + 8, 400 + 8), 0xF87800)  # dragon patch
    paint(s, (610 - 8, 410 - 8, 610 + 8, 410 + 8), 0x00A8B0)  # same icon as the pink one
    assert _near(map_missions.available_icons(FakeCtx([s])), [(600, 400), (900, 400), (1200, 400)])


def _in_band(clicks, x1, y1, x2, y2):
    return any(x1 <= x <= x2 and y1 <= y <= y2 for x, y in clicks)


def _near(points, expected, tol=4):
    return len(points) == len(expected) and all(
        abs(px - ex) <= tol and abs(py - ey) <= tol for (px, py), (ex, ey) in zip(sorted(points), sorted(expected))
    )


def _clicked_near(clicks, x, y, tol=4):
    return any(abs(cx - x) <= tol and abs(cy - y) <= tol for cx, cy in clicks)


def test_collect_loop_bounded():
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.MR_MISSION_DONE.rect, 0x0AA008)
    c = FakeCtx([s] * 60)
    map_missions.run(c, Config())
    assert c.clicks.count((162, 334)) == 10 and c.keys[0] == "m"


def test_collect_presses_okay():
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.MR_MISSION_DONE.rect, 0x0AA008)
    popup = s.copy()
    paint(popup, (805, 598, 1114, 668), 0x0AA008)
    c = FakeCtx([s, popup] + [_map()] * 10)
    map_missions.run(c, Config())
    assert _in_band(c.clicks, 805, 598, 1114, 668)


def test_detects_icons_and_starts_free_mission_only():
    s = _map()
    paint(s, atlas.MAP_IDLE_BANNER.rect, 0x542710)
    _icon(s, 1105, 501)
    popup = s.copy()
    paint(popup, (958, 830, 1208, 900), 0x0AA008)
    paid = popup.copy()
    paint(paid, (1000, 850, 1020, 870), 0xC040E0)
    assert _near(map_missions.available_icons(FakeCtx([s])), [(1105, 501)])
    c = FakeCtx([s, popup] + [_map()] * 20)
    map_missions.run(c, Config())
    assert _clicked_near(c.clicks, 1105, 501) and _in_band(c.clicks, 958, 830, 1208, 900)
    c2 = FakeCtx([s, paid] + [_map()] * 20)
    map_missions.run(c2, Config())
    assert not _in_band(c2.clicks, 958, 830, 1208, 900)


def test_no_start_pass_without_idle_banner():
    s = _map()
    _icon(s, 1105, 501)
    c = FakeCtx([s] * 5)
    map_missions.run(c, Config())
    assert not _clicked_near(c.clicks, 1105, 501)


def test_free_refresh_only_without_gem():
    s = _map()
    paint(s, atlas.MR_FREE_RESET.rect, 0xFCAC47)
    c = FakeCtx([s] * 5)
    map_missions.run(c, Config())
    assert (173, 918) in c.clicks
    paid = s.copy()
    paint(paid, (150, 900, 170, 920), 0xC040E0)
    c2 = FakeCtx([paid] * 5)
    map_missions.run(c2, Config())
    assert (173, 918) not in c2.clicks
