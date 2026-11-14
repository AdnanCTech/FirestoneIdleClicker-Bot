from datetime import datetime

from firestone_clicker import schedule


def test_window_is_the_latest_boundary_before_now():
    hours = [1, 13]
    assert schedule.window(hours, datetime(2026, 11, 11, 13, 5)) == "2026-11-11 13"
    assert schedule.window(hours, datetime(2026, 11, 11, 12, 59)) == "2026-11-11 01"
    assert schedule.window(hours, datetime(2026, 11, 11, 0, 30)) == "2026-11-10 13"
    assert schedule.window([9], datetime(2026, 11, 11, 8, 59)) == "2026-11-10 09"


def test_state_remembers_done_windows_across_loads(tmp_path):
    p = tmp_path / "state.json"
    s = schedule.State(p)
    assert not s.done("arena", "2026-11-11 13")
    s.mark("arena", "2026-11-11 13")
    assert schedule.State(p).done("arena", "2026-11-11 13")
    assert not schedule.State(p).done("arena", "2026-11-12 01")


def test_unreadable_state_file_starts_empty(tmp_path):
    p = tmp_path / "state.json"
    p.write_text("{not json", encoding="utf-8")
    assert not schedule.State(p).done("arena", "x")


def test_due_when_never_claimed_or_the_interval_has_passed():
    now = datetime(2026, 11, 14, 13, 0)
    assert schedule.due(None, 6, now)
    assert schedule.due("2026-11-14T06:59:00", 6, now)
    assert not schedule.due("2026-11-14T07:01:00", 6, now)
    assert schedule.due("2026-11-14 07", 6, now)  # an old window name counts as that hour
    assert not schedule.due("2026-11-14 08", 6, now)
    assert schedule.due("junk", 6, now)
