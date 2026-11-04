from conftest import blank, paint

from firestone_clicker import atlas
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx
from firestone_clicker.features import guild


def _guild_screen():
    s = blank()
    paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    return s


def test_expeditions_claims_and_starts_on_dot():
    s = _guild_screen()
    paint(s, atlas.GUILD_EXPEDITION_DOT.rect, 0xF41000)
    # Dot visible through open, claim, start, close; gone afterwards.
    c = FakeCtx([s] * 4 + [_guild_screen()])
    guild.expeditions(c)
    assert c.clicks.count((1321, 331)) == 2


def test_expeditions_one_more_start_if_dot_persists():
    s = _guild_screen()
    paint(s, atlas.GUILD_EXPEDITION_DOT.rect, 0xF41000)
    c = FakeCtx([s] * 10)
    guild.expeditions(c)
    assert c.clicks.count((1321, 331)) == 3


def test_expeditions_noop_without_dot():
    c = FakeCtx([_guild_screen()])
    guild.expeditions(c)
    assert (308, 406) not in c.clicks


def test_awaken_walks_multipliers_then_auto():
    s = _guild_screen()
    paint(s, atlas.AWAKEN_DOT.rect, 0xF41000)
    paint(s, atlas.AWAKEN_BUTTON_ORANGE.rect, 0xF4A044)
    paint(s, (1727, 632, 1815, 692), 0x0A9F05)  # x80 available
    s2 = s.copy()
    paint(s2, atlas.AWAKEN_AUTO_READY.rect, 0x0A9F05)
    c = FakeCtx([s, s, s, s2, s2, s2])
    guild.awaken(c)
    assert (1772, 666) in c.clicks and (1774, 993) in c.clicks


def test_awaken_green_single():
    s = _guild_screen()
    paint(s, atlas.AWAKEN_DOT.rect, 0xF41000)
    paint(s, atlas.AWAKEN_BUTTON_GREEN.rect, 0x0A9F05)
    c = FakeCtx([s] * 4)
    guild.awaken(c)
    assert (1725, 582) in c.clicks


def _ptree_cfg(*nodes):
    cfg = Config()
    for k in cfg.ptree:
        cfg.ptree[k] = k in nodes
    return cfg


def _node_popup():
    s = blank()
    paint(s, atlas.PTREE_POPUP.rect, 0x295484)
    paint(s, atlas.PTREE_BUY_RECT, 0x0BA108)
    return s


def test_ptree_buys_enabled_node_and_closes_popup():
    tree = blank()
    # open entry, open tree, node click -> popup, buy -> popup gone, close
    c = FakeCtx([tree, tree, tree, _node_popup(), tree, tree])
    guild.ptree(c, _ptree_cfg("AttDmg"))
    assert (365, 313) in c.clicks and (960, 686) in c.clicks
    assert (512, 276) not in c.clicks


def test_ptree_skips_node_without_popup():
    tree = blank()
    c = FakeCtx([tree] * 6)
    guild.ptree(c, _ptree_cfg("AttDmg"))
    assert (365, 313) in c.clicks and (960, 686) not in c.clicks


def test_ptree_gem_on_buy_is_skipped():
    popup = _node_popup()
    paint(popup, (950, 680, 970, 700), 0xC040E0)
    c = FakeCtx([blank(), blank(), blank(), popup, popup, popup])
    guild.ptree(c, _ptree_cfg("AttDmg"))
    assert (960, 686) not in c.clicks


def test_ptree_need_more_closes_and_stops():
    need = _node_popup()
    paint(need, atlas.PTREE_NEED_MORE.rect, 0xFAF3E1)
    # entry, open, node -> popup, buy -> need-more, X -> popup, close -> tree
    c = FakeCtx([blank(), blank(), blank(), _node_popup(), need, _node_popup(), blank()])
    guild.ptree(c, _ptree_cfg("AttDmg", "AttHp"))
    assert (1283, 349) in c.clicks and (1239, 284) in c.clicks
    assert (512, 276) not in c.clicks  # second node never attempted


def test_run_visits_guild_once_and_closes():
    s = _guild_screen()
    cfg = Config()
    cfg.features["awaken"] = cfg.features["ptree"] = False
    c = FakeCtx([s] * 8)
    guild.run(c, cfg)
    assert c.clicks[0] == (1857, 481) and c.clicks[-1] == (1851, 84)
