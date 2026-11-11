from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import engineer

CLAIM = (1530, 666, 1750, 751)  # "Tools production" Claim, live 2026-11-11 (grey with a countdown then)


def _main():
    s = blank()
    paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    return s


def _popup():
    s = _main()
    paint(s, atlas.ENG_POPUP_X.rect, 0xFFF9CE)
    return s


def _engineer(ready):
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.ENG_OPEN.rect, 0xE1CEAD)
    paint(s, CLAIM, 0x0BA108 if ready else 0x9FA19F)
    paint(s, (1600, 700, 1680, 720), 0xFFFFFF)
    return s


def _claimed(clicks):
    return [p for p in clicks if 1530 <= p[0] <= 1750 and 666 <= p[1] <= 751]


def test_grey_claim_with_countdown_is_not_ready():
    c = FakeCtx([_main(), _popup(), _engineer(False)] + [_main()] * 10)
    assert engineer.run(c, Config()) is False
    assert "engineer: not ready" in c.logs and not _claimed(c.clicks)
    assert (1262, 910) in c.clicks and (600, 532) in c.clicks


def test_green_claim_is_pressed_once():
    c = FakeCtx([_main(), _popup(), _engineer(True)] + [_engineer(False)] * 10)
    assert engineer.run(c, Config()) is True
    assert len(_claimed(c.clicks)) == 1 and "engineer: claimed" in c.logs


def test_claim_with_a_gem_is_skipped():
    paid = _engineer(True)
    paint(paid, (1560, 690, 1580, 710), 0xC040E0)
    c = FakeCtx([_main(), _popup(), paid] + [paid] * 10)
    assert engineer.run(c, Config()) is False and not _claimed(c.clicks)


def test_engineer_card_not_opening_retries_later():
    c = FakeCtx([_main(), _popup(), _popup()] + [_popup()] * 10)
    assert engineer.run(c, Config()) is False and not _claimed(c.clicks)
