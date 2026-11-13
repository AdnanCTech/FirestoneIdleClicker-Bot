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


def test_stand_cut_off_by_the_idle_banner_still_counts():
    # Measured live 2026-11-04: the naval icon's stand at y 964..975 is half hidden by the
    # "squads are idling" banner, exactly when there is something to start. Only its top 7 rows
    # show, which is under the normal pixel minimum.
    s = _map()
    paint(s, (1040 - 25, 929 - 25, 1040 + 25, 929 + 25), 0x135696)
    paint(s, (1032, 964, 1047, 971), 0xE6DDB5)
    assert _near(map_missions.available_icons(FakeCtx([s])), [(1040, 929)])


def test_tiny_beige_specks_are_not_icons():
    s = _map()
    paint(s, (800, 500, 806, 506), 0xE6DDB5)  # 7x7 speck, as seen on the mountains
    paint(s, (1460, 360, 1470, 366), 0xE6DDB5)  # 11x7 sliver away from the bottom edge
    assert map_missions.available_icons(FakeCtx([s])) == []


def test_icon_on_celenis_at_the_right_edge_detected():
    # Measured live 2026-11-06: the Dragon mission on Celenis has its stand at x 1716..1727,
    # past the old 1700 scan limit; the side button panel starts at x 1775.
    s = _map()
    _icon(s, 1721, 653, 0xF05800)
    assert _near(map_missions.available_icons(FakeCtx([s])), [(1721, 653)])


def test_idle_banner_gradient_is_not_a_row_of_pins():
    # Measured live 2026-11-06: the banner's cream gradient (top at y 944 that day, 971 the day
    # before) matches the stand colour in its lower rows, and the gaps between its letters
    # looked like a row of 11 px stands. A real stand cut off by the banner must still count.
    s = _map()
    for y in range(944, 996):
        paint(s, (462, y, 1240, y + 1), 0xFBE9D2 if y < 964 else 0xEFD7BD)
    for x in range(520, 1200, 20):  # dark letters leaving 11 px cream gaps
        paint(s, (x, 955, x + 9, 985), 0x3A2415)
    paint(s, (1032, 937, 1047, 944), 0xE6DDB5)  # stand with only 7 rows above the banner
    paint(s, (1040 - 25, 902 - 25, 1040 + 25, 902 + 25), 0x135696)
    assert _near(map_missions.available_icons(FakeCtx([s])), [(1040, 902)])


SCOUT_PIN = (  # the Scout mission's pin stand, pixel for pixel, live 2026-11-06 at x 792, y 451
    "################",
    ".#############..",
    "..############..",
    "..###########...",
    "...##########...",
    "...#########....",
    "....#######.....",
    ".....######.....",
    ".....#####......",
    "......####......",
    ".......##.......",
    ".......#........",
)


def _pin(s, left, top, bitmap=SCOUT_PIN):
    for dy, row in enumerate(bitmap):
        for dx, ch in enumerate(row):
            if ch == "#":
                paint(s, (left + dx, top + dy, left + dx, top + dy), 0xE6DDB5)


def test_real_shaped_stand_detected_whatever_the_cell_alignment():
    # The 4 px cell grid trims the pin's thin tail: in 6 of 8 live frames the blob was only
    # 7 rows tall and the old height filter dropped the Scout mission.
    for left, top in ((792, 451), (793, 452), (794, 451), (792, 453)):
        s = _map()
        paint(s, (left + 8 - 25, top - 60, left + 8 + 25, top - 10), 0xF07070)
        _pin(s, left, top)
        got = map_missions.available_icons(FakeCtx([s]))
        assert _near(got, [(left + 8, top - atlas.MAP_ICON_ABOVE_STAND)]), (left, top, got)


def _titan(s, x, y):
    # Volcano disc measured live 2026-11-12 at (1321,152): deep blue sky in the top rows of the
    # sample window (0x005090, 93 px vs <=3 on every other icon) over lava orange (0xF08000,
    # 93 px; the dragon has 106 of the same orange but no sky). It sits over the sea, so the
    # wheel's cyan key also matches it (85 px) and the titan must be checked first.
    paint(s, (x - 25, y - 25, x + 25, y + 25), 0x18B8F0)
    paint(s, (x - 25, y - 40, x + 25, y - 10), 0x005090)
    paint(s, (x - 25, y - 10, x + 25, y + 15), 0xF08000)
    paint(s, (x - 9, y + 35, x + 9, y + 45), 0xE6DDB5)


def test_titan_volcano_is_opened_before_every_other_kind():
    s = _map()
    _icon(s, 1200, 300, 0xF060F0)  # paw, highest on the map
    _icon(s, 600, 500, 0xF05800)  # dragon: lava orange but no sky
    _titan(s, 1320, 700)
    got = map_missions.available_icons(FakeCtx([s]))
    want = [(1320, 700), (1200, 300), (600, 500)]
    assert len(got) == len(want) and all(abs(gx - wx) <= 4 and abs(gy - wy) <= 4 for (gx, gy), (wx, wy) in zip(got, want))


def test_sky_blue_disc_without_lava_is_not_a_titan():
    s = _map()
    _icon(s, 800, 400, 0x005090)  # navy disc only
    _icon(s, 1200, 400, 0xF060F0)  # paw
    assert _near(map_missions.available_icons(FakeCtx([s])), [(1200, 400), (800, 400)])


def _banner_map():
    s = _map()
    paint(s, atlas.MAP_IDLE_BANNER.rect, 0x542710)
    return s


def _start_popup(s):
    p = s.copy()
    paint(p, (958, 830, 1208, 900), 0x0AA008)
    return p


def test_sweep_pans_the_map_when_the_banner_outlives_the_visible_pass(monkeypatch):
    monkeypatch.setattr(map_missions, "_next_sweep", 0.0)
    empty = _banner_map()
    hidden = _banner_map()
    paint(hidden, (400, 150, 1700, 900), 0x2A7A3A)  # land where the empty view had sea: a real pan
    _icon(hidden, 1105, 501)
    corner = 2 * atlas.MAP_PAN_MAX  # the corner is always MAP_PAN_MAX drags up and left (clamped at the edges)
    # m -> empty view (banner, no icons): corner drags -> same, pan right -> hidden icon,
    # icon -> start popup, start -> map without banner.
    c = FakeCtx([empty] + [empty.copy() for _ in range(corner)] + [hidden, _start_popup(hidden), _map()] + [_map()] * 14)
    map_missions.run(c, Config())
    assert _clicked_near(c.clicks, 1105, 501) and _in_band(c.clicks, 958, 830, 1208, 900)
    assert len(c.drags) == corner + 1 + corner + 2  # sweep: corner, one view right; home: corner, fixed left, fixed up
    hx, hy = atlas.MAP_HOME_DRAG
    assert c.drags[-2][2] - c.drags[-2][0] == -hx and c.drags[-1][3] - c.drags[-1][1] == -hy
    assert c.drags[0][3] > c.drags[0][1]  # first drag pulls the map down to reveal what is above
    assert c.drags[corner][2] < c.drags[corner][0]  # after the corner, a drag left reveals what is right


def test_fruitless_sweep_is_bounded_and_not_repeated_for_a_while(monkeypatch):
    monkeypatch.setattr(map_missions, "_next_sweep", 0.0)
    empty = _banner_map()
    c = FakeCtx([empty.copy() for _ in range(12)])
    map_missions.run(c, Config())
    # corner, then a right and a down drag that change nothing end the sweep; corner and home drags after
    corner = 2 * atlas.MAP_PAN_MAX
    assert len(c.drags) == corner + 2 + corner + 2 and all(p == (atlas.BIG_CLOSE.x, atlas.BIG_CLOSE.y) for p in c.clicks)
    assert "map: sweep found nothing" in c.logs
    c2 = FakeCtx([empty.copy() for _ in range(4)])
    map_missions.run(c2, Config())
    assert not c2.drags and "map: sweep skipped, last one found nothing" in c2.logs


def test_pan_starts_away_from_icons():
    s = _banner_map()
    x, y = atlas.MAP_PAN_STARTS["up"][0]
    _icon(s, x, y)
    c = FakeCtx([s, s.copy()])
    assert map_missions._pan(c, "up", [(x, y)]) is False
    sx, sy = c.drags[0][:2]
    assert abs(sx - x) > atlas.MAP_PAN_CLEAR or abs(sy - y) > atlas.MAP_PAN_CLEAR


def test_a_few_brown_specks_in_the_banner_band_are_not_the_idle_banner():
    # Live 2026-11-12: the default map view with no banner had 6 brown pixels in the probe band
    # (2834 with the banner showing) and the bot opened all 13 popups every cycle.
    s = _map()
    _icon(s, 1105, 501)
    x1, y1 = atlas.MAP_IDLE_BANNER.rect[:2]
    paint(s, (x1 + 200, y1 + 5, x1 + 202, y1 + 7), 0x542710)
    c = FakeCtx([s] * 5)
    map_missions.run(c, Config())
    assert not _clicked_near(c.clicks, 1105, 501)
    assert "map: no idle squads, start pass skipped" in c.logs


def _dialog(s):
    """A dialog with the popup X in the corner band and no idle banner showing."""
    d = _map()
    paint(d, (1470, 210, 1520, 260), 0xFF6109)
    paint(d, (1488, 228, 1504, 244), 0xFFF9CE)
    return d


def test_dialog_left_open_after_a_start_is_closed_and_the_pass_goes_on():
    s = _banner_map()
    _icon(s, 600, 400)
    _icon(s, 1100, 500)
    # m, icon -> start popup, start -> a dialog stays open (banner hidden), its X -> map with
    # banner, second icon -> start popup, start -> map without banner.
    c = FakeCtx([s, _start_popup(s), _dialog(s), s, _start_popup(s), _map()] + [_map()] * 10)
    map_missions.run(c, Config())
    assert _clicked_near(c.clicks, 600, 400) and _clicked_near(c.clicks, 1495, 235) and _clicked_near(c.clicks, 1100, 500)
    assert "map: 2 started, 0 popups closed (in progress or not startable)" in c.logs and not c.drags


def test_banner_gone_after_nothing_started_is_captured():
    s = _banner_map()
    _icon(s, 600, 400)
    _icon(s, 1100, 500)
    nopop = _map()  # the click opened nothing a popup check knows and the banner is gone
    c = FakeCtx([s, nopop] + [_map()] * 10)
    map_missions.run(c, Config())
    assert "map: no more idle squads" in c.logs and c.saved == ["diag/map_banner_gone.png"]
    assert not _clicked_near(c.clicks, 1100, 500)
