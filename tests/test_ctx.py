import pytest
from conftest import blank, paint

from firestone_clicker import vision, win
from firestone_clicker.ctx import FakeCtx, LiveCtx, Stopped


def test_fake_ctx_advances_on_click():
    a, b = blank(), blank()
    paint(b, (0, 0, 5, 5), 0xFF0000)
    c = FakeCtx([a, b])
    assert not vision.any_match(c.grab((0, 0, 5, 5)), 0xFF0000, 0)
    c.click(1, 1)
    assert vision.any_match(c.grab((0, 0, 5, 5)), 0xFF0000, 0)
    assert c.clicks == [(1, 1)]


def test_sleep_aborts_on_stop():
    c = LiveCtx(dry_run=True)
    c.stop.set()
    with pytest.raises(Stopped):
        c.sleep(20000)


def test_client_rect_rejects_wrong_size():
    with pytest.raises(win.BadWindow):
        win.check_client((0, 31, 1600, 900))
    win.check_client((0, 31, 1920, 1009))
