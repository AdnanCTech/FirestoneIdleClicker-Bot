from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import guardian


def _quarter():
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    return s


def test_guardian_evolve_and_train():
    s = _quarter()
    paint(s, atlas.GUARDIAN_EVOLVE_DOT.rect, 0xF41000)
    paint(s, atlas.GUARDIAN_TRAIN_READY.rect, 0x0AA008)
    cfg = Config()
    cfg.guardian_train_target = 3
    c = FakeCtx([s] * 10)
    guardian.run(c, cfg)
    assert (1117, 750) in c.clicks and (1138, 787) in c.clicks
    assert c.keys.count("right") == 2 and ("left", 2000) in c.key_holds


def test_guardian_train_skips_paid():
    s = _quarter()
    paint(s, atlas.GUARDIAN_TRAIN_READY.rect, 0x0AA008)
    paint(s, (1100, 775, 1120, 800), 0xC040E0)
    c = FakeCtx([s] * 10)
    guardian.run(c, Config())
    assert (1138, 787) not in c.clicks


def test_guardian_nothing_to_do_still_closes():
    c = FakeCtx([_quarter()] * 6)
    guardian.run(c, Config())
    assert (1117, 750) not in c.clicks and c.clicks[-1] == (1851, 84)
