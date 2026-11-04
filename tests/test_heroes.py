from conftest import blank, paint

from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import heroes


def test_heroes_clicks_enabled_green_slots():
    s = blank()
    paint(s, (1862, 434, 1888, 469), 0x0AA008)  # H1 ready
    c = FakeCtx([s, s])
    heroes.run(c, Config())
    assert c.keys[0] == "u" and (1670, 427) in c.clicks and c.clicks[-1] == (1851, 84)


def test_heroes_skips_disabled():
    s = blank()
    paint(s, (1862, 434, 1888, 469), 0x0AA008)
    cfg = Config()
    cfg.heroes["h1"] = False
    c = FakeCtx([s, s])
    heroes.run(c, cfg)
    assert (1670, 427) not in c.clicks
    assert any(m.startswith("heroes: 0 upgraded, 6 not green") and "1 off" in m for m in c.logs)


def test_heroes_skips_paid():
    s = blank()
    paint(s, (1862, 434, 1888, 469), 0x0AA008)
    paint(s, (1600, 415, 1740, 440), 0xC040E0)
    c = FakeCtx([s, s])
    heroes.run(c, Config())
    assert (1670, 427) not in c.clicks
