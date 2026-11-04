from pathlib import Path

from conftest import blank, paint

from firestone_clicker import atlas, check, paths
from firestone_clicker.atlas import Probe
from firestone_clicker.ctx import FakeCtx


def test_base_dir_is_cwd_when_not_frozen(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delattr("sys.frozen", raising=False)
    assert paths.base_dir() == tmp_path


def test_base_dir_is_exe_folder_when_frozen(monkeypatch, tmp_path):
    exe = tmp_path / "bin" / "FirestoneClicker.exe"
    exe.parent.mkdir()
    monkeypatch.setattr("sys.frozen", True, raising=False)
    monkeypatch.setattr("sys.executable", str(exe))
    assert paths.base_dir() == exe.parent


def test_ensure_settings_writes_default_once(tmp_path):
    p = tmp_path / "settings.toml"
    assert paths.ensure_settings(p) is True
    text = p.read_text(encoding="utf-8")
    assert "[features]" in text and "oracle = true" in text
    p.write_text("delay_s = 5\n", encoding="utf-8")
    assert paths.ensure_settings(p) is False
    assert p.read_text(encoding="utf-8") == "delay_s = 5\n"


def test_atlas_probes_lists_named_probes():
    items = dict(check.atlas_probes())
    assert "DIALOG_CLOSE_X" in items and isinstance(items["DIALOG_CLOSE_X"], Probe)
    assert any(k.startswith("ALCHEMY_SLOTS") for k in items)


def test_report_marks_found_and_missing():
    s = blank()
    paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    lines = check.report(FakeCtx([s]), [("TOWN_OPEN", atlas.TOWN_OPEN), ("DIALOG_CLOSE_X", atlas.DIALOG_CLOSE_X)])
    assert lines == ["FOUND   TOWN_OPEN", "missing DIALOG_CLOSE_X"]
