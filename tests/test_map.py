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


def _icon(s, x, y, disc=0xF07070):
    # Any mission icon: a coloured disc with the beige pin stand 35 px below its click point.
    # Measured live 2026-11-04: 50 px above the stand sat under an animated flag of the
    # in-progress icon above and opened the wrong popup 1 time in 3; 35 px was 10 for 10.
    paint(s, (x - 25, y - 25, x + 25, y + 25), disc)
    paint(s, (x - 9, y + 35, x + 9, y + 45), 0xE6DDB5)


def test_icons_found_by_pin_stand_whatever_the_disc_colour():
    s = _map()
    _icon(s, 600, 400)  # sword pink
    _icon(s, 900, 400, 0x135696)  # naval wheel: disc is sea blue, only the stand gives it away
    _icon(s, 1200, 400, 0xA040D0)  # monster paw purple
    paint(s, (1400 - 25, 400 - 25, 1400 + 25, 400 + 25), 0xF07070)  # pink blob with no stand: not an icon
    assert _near(map_missions.available_icons(FakeCtx([s])), [(600, 400), (900, 400), (1200, 400)])


def test_icon_stand_near_bottom_edge_detected():
    # Measured live 2026-11-04: the naval icon at (1040,905) has its stand at y 914..925,
    # below the old 940 scan limit once the 50 px offset is accounted for.
    s = _map()
    _icon(s, 1040, 905, 0x135696)
    assert _near(map_missions.available_icons(FakeCtx([s])), [(1040, 905)])


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


def test_close_popup_uses_top_right_x_not_avatar_ring():
    s = _map()
    paint(s, (940, 215, 1000, 275), 0xFF6109)  # avatar ring, centre of popup header
    paint(s, (960, 235, 980, 255), 0xFFF9CE)
    paint(s, (1470, 210, 1520, 260), 0xFF6109)  # the real X, top right
    paint(s, (1488, 228, 1504, 244), 0xFFF9CE)
    c = FakeCtx([s] * 3)
    map_missions._close_popup(c)
    assert len(c.clicks) == 1 and abs(c.clicks[0][0] - 1495) <= 4 and abs(c.clicks[0][1] - 235) <= 4


def test_in_progress_popup_does_not_block_next_icon():
    s = _map()
    paint(s, atlas.MAP_IDLE_BANNER.rect, 0x542710)
    _icon(s, 600, 400)
    _icon(s, 1100, 500)
    inprog = s.copy()  # popup with avatar ring and corner X but no green button
    paint(inprog, (940, 215, 1000, 275), 0xFF6109)
    paint(inprog, (960, 235, 980, 255), 0xFFF9CE)
    paint(inprog, (1470, 210, 1520, 260), 0xFF6109)
    paint(inprog, (1488, 228, 1504, 244), 0xFFF9CE)
    start = s.copy()
    paint(start, (958, 830, 1208, 900), 0x0AA008)
    # m, first icon -> in-progress popup, X -> map, second icon -> start popup, start -> map
    c = FakeCtx([s, inprog, s, start] + [_map()] * 10)
    map_missions.run(c, Config())
    assert _clicked_near(c.clicks, 1100, 500) and _in_band(c.clicks, 958, 830, 1208, 900)


def test_no_start_pass_without_idle_banner():
    s = _map()
    _icon(s, 1105, 501)
    c = FakeCtx([s] * 5)
    map_missions.run(c, Config())
    assert not _clicked_near(c.clicks, 1105, 501)
    assert "map: no idle squads, start pass skipped" in c.logs


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


def test_priority_icons_come_first_then_the_rest_top_down():
    # Keys measured live 2026-11-04 in a 28x50 window above the stand: paw magenta glow
    # (~150 px vs 0 elsewhere), wheel cyan highlights (96 vs <=3), dragon deep orange (55+ vs <=2).
    s = _map()
    _icon(s, 600, 300)  # sword, highest on the map
    _icon(s, 1300, 350, 0xF05800)  # dragon
    _icon(s, 700, 500)  # telescope-ish, plain
    _icon(s, 1000, 600, 0x18B8F0)  # wheel
    _icon(s, 1200, 800, 0xF060F0)  # paw, lowest on the map
    got = map_missions.available_icons(FakeCtx([s]))
    want = [(1200, 800), (1000, 600), (1300, 350), (600, 300), (700, 500)]
    assert len(got) == len(want) and all(abs(gx - wx) <= 4 and abs(gy - wy) <= 4 for (gx, gy), (wx, wy) in zip(got, want))
