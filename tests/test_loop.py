from conftest import blank, paint

from firestone_clicker import atlas, loop
from firestone_clicker.config import Config
from firestone_clicker.ctx import FakeCtx


def _home_ok():
    s = blank()
    paint(s, atlas.MM_SETTINGS_OPEN.rect, 0x285483)
    return s


def test_run_cycle_runs_enabled_only(monkeypatch):
    calls = []
    monkeypatch.setattr(
        loop, "FEATURES", [("a", lambda c, f: calls.append("a")), ("b", lambda c, f: calls.append("b"))]
    )
    cfg = Config()
    cfg.features.update({"a": True, "b": False})
    loop.run_cycle(FakeCtx([_home_ok()] * 5), cfg)
    assert calls == ["a"]


def test_once_runs_only_that_feature(monkeypatch):
    calls = []
    monkeypatch.setattr(
        loop, "FEATURES", [("a", lambda c, f: calls.append("a")), ("b", lambda c, f: calls.append("b"))]
    )
    cfg = Config()
    cfg.features.update({"a": True, "b": True})
    loop.run_cycle(FakeCtx([_home_ok()] * 5), cfg, only="b")
    assert calls == ["b"]


def test_feature_exception_is_contained(monkeypatch):
    def boom(c, f):
        raise RuntimeError("x")

    monkeypatch.setattr(loop, "FEATURES", [("a", boom)])
    cfg = Config()
    cfg.features["a"] = True
    c = FakeCtx([_home_ok()] * 20)
    assert loop.run_cycle(c, cfg) is True
    assert any("a failed" in m for m in c.logs)


def test_loop_exits_after_three_home_failures(monkeypatch):
    monkeypatch.setattr(loop, "FEATURES", [])
    cfg = Config()
    cfg.delay_s = 0
    c = FakeCtx([blank()] * 200)
    loop.main(c, cfg, once=None)
    assert c.logs[-1].startswith("exit: go_home failed 3")


def test_main_exits_when_window_check_fails(monkeypatch):
    calls = []
    monkeypatch.setattr(loop, "FEATURES", [("a", lambda c, f: calls.append("a"))])
    cfg = Config()
    cfg.features["a"] = True
    c = FakeCtx([_home_ok()] * 20)
    assert loop.main(c, cfg, once=None, window_ok=lambda: False) is False
    assert calls == [] and c.logs[-1].startswith("exit: game window")


def test_main_returns_false_after_home_failures(monkeypatch):
    monkeypatch.setattr(loop, "FEATURES", [])
    cfg = Config()
    cfg.delay_s = 0
    assert loop.main(FakeCtx([blank()] * 200), cfg, once=None) is False


def test_main_returns_true_after_once(monkeypatch):
    monkeypatch.setattr(loop, "FEATURES", [("a", lambda c, f: None)])
    assert loop.main(FakeCtx([_home_ok()] * 20), Config(), once="a") is True


def test_ctrl_c_exits_cleanly(monkeypatch):
    def interrupt(c, f):
        raise KeyboardInterrupt

    monkeypatch.setattr(loop, "FEATURES", [("a", interrupt)])
    cfg = Config()
    cfg.features["a"] = True
    c = FakeCtx([_home_ok()] * 5)
    assert loop.main(c, cfg, once=None) is True
    assert c.logs[-1] == "exit: Ctrl+C"


def test_guild_entry_gated_by_any_of_three(monkeypatch):
    cfg = Config()
    for k in ("expeditions", "awaken", "ptree"):
        cfg.features[k] = False
    assert loop.enabled("guild", cfg) is False
    cfg.features["awaken"] = True
    assert loop.enabled("guild", cfg) is True
