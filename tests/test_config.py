import pytest

from firestone_clicker import config


def test_defaults_when_missing(tmp_path):
    c = config.load(tmp_path / "nope.toml")
    assert c.delay_s == 60 and all(c.features.values()) and c.guardian_train_target == 1
    assert len(c.ptree) == 20 and all(c.ptree.values())


def test_override(tmp_path):
    (tmp_path / "s.toml").write_text(
        "delay_s = 5\n[features]\nresearch = false\n[guardian]\ntrain_target = 3\n"
    )
    c = config.load(tmp_path / "s.toml")
    assert c.delay_s == 5 and c.features["research"] is False and c.guardian_train_target == 3


def test_rejects_bad_train_target(tmp_path):
    (tmp_path / "s.toml").write_text("[guardian]\ntrain_target = 7\n")
    with pytest.raises(ValueError):
        config.load(tmp_path / "s.toml")
