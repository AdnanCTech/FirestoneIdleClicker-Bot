# Firestone Clicker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A minimal Windows Python bot that loops eight Firestone Idle RPG automations (guild expeditions, awakening, personal tree, map missions, alchemist, research, hero upgrades, guardian) using pixel probes and simulated input, never spending gems.

**Architecture:** A `Ctx` object owns the four side effects (grab pixels, click, key, sleep) so every feature is a plain function `run(ctx, cfg)` testable against painted numpy screens. `atlas.py` holds every coordinate. `nav.py` holds the shared navigation (go home, open town, safe click). `__main__.py` is the loop.

**Tech Stack:** Python 3.12, `uv`, deps `mss`, `numpy`, `pynput`, `psutil`; dev dep `pytest`. Settings in `settings.toml` via stdlib `tomllib`.

**Spec:** `F:\Code\FireStoneClicker\docs\superpowers\specs\2026-11-04-firestone-clicker-design.md`

**Reference source snapshot** (copy constants from here, verbatim): `C:\Users\Adnan\fsb_src\vision__atlas.py`, `features__*.py`, `vision__buttons.py`, `vision__probes.py`.

## Global Constraints

- Windows 11 only. Epic build. 1920x1080, 100% DPI, game windowed and maximized, English. Client rect 1920x1009; logical coordinates equal screen coordinates when the client origin is (0, 31).
- Python 3.12. Runtime deps exactly: mss, numpy, pynput, psutil. No others.
- Target under ~800 lines of non-test code.
- Every button that could spend anything goes through `safe_click` (gem check) before the click.
- The bot never drags, zooms or scrolls the world map.
- No OCR, no template matching, no GUI, no relaunch.
- Comments: none that restate the code; a short "why" is fine.

## Review Focus

1. A probe rect with inverted corners (e.g. `GUILD_EXPEDITION_DOT` is `450,410,380,490` in the source) must still match. Pinned by `test_probe_inverted_corners` in Task 1.
2. The game window is present but smaller than 1920x1009 (not maximized). The bot must refuse to start rather than click wrong spots. Pinned by `test_client_rect_rejects_wrong_size` in Task 3.
3. A popup that `go_home` cannot clear must not spin forever: bounded closes, and the loop exits after 3 consecutive failures. Pinned by `test_go_home_gives_up` in Task 4 and `test_loop_exits_after_three_home_failures` in Task 11.
4. A gem-priced button must never be clicked even when the green/orange probe says "ready". Pinned by `test_safe_click_skips_gem` in Task 4 and by each feature's `*_skips_paid` test.
5. Win+Esc during a long settle (awaken auto settles 20 s) must stop within 0.1 s. Pinned by `test_sleep_aborts_on_stop` in Task 3.

---

### Task 1: Project scaffold, atlas primitives, pixel matching

**Files:**
- Create: `pyproject.toml`, `firestone_clicker/__init__.py`, `firestone_clicker/atlas.py`, `firestone_clicker/vision.py`, `tests/conftest.py`, `tests/test_vision.py`

**Interfaces:**
- Produces: `atlas.Point(x:int, y:int)`, `atlas.Probe(x1,y1,x2,y2,color:int,var:int=3,name:str="")` with `.rect -> tuple[int,int,int,int]` (normalised, inclusive). Colour constants: `RED_DOT=0xF41000`, `RED_DOT_VAR=32`, `GREEN_BUTTON=0x0AA008`, `GREEN_BUTTON_2=0x16BC15`, `ORANGE_1=0xF9AA47`, `ORANGE_2=0xFCAC47`, `IDLE_TROOP=0x542710`, `AWAKEN_GREEN=0x0A9F05`, `DIALOG_RING=0xFF6109`, `DIALOG_X_CROSS=0xFFF9CE`. `REF_ORIGIN=(0,31)`, `REF_SIZE=(1920,1009)`.
- Produces: `vision.match_mask(img: np.ndarray, color: int, var: int) -> np.ndarray[bool]` (img is BGRA HxWx4), `vision.any_match(img, color, var) -> bool`, `vision.green_boxes(img, origin: tuple[int,int], min_w=100, min_h=25, var=30) -> list[tuple[int,int,int,int]]` (logical rects, left to right), `vision.gem_share(img) -> float` (fraction of pixels with R>120, B>120, G<R-60, G<B-60), `vision.color_share(img, color, var) -> float`.
- Test helper in conftest: `blank() -> np.ndarray` (1080x1920x4 uint8 zeros, alpha 255) and `paint(img, rect, color)` filling an inclusive logical rect with 0xRRGGBB as BGRA.

- [ ] **Step 1: Write `pyproject.toml`** with `[project]` name `firestone-clicker`, `requires-python = ">=3.12"`, dependencies `mss`, `numpy`, `pynput`, `psutil`; `[dependency-groups] dev = ["pytest"]`; `[tool.pytest.ini_options] testpaths = ["tests"]`. Run `uv sync` and confirm `uv run python -c "import mss, numpy, pynput, psutil"` prints nothing.

- [ ] **Step 2: Write failing tests** in `tests/test_vision.py`:

```python
def test_match_mask_exact_and_tolerance():
    img = blank(); paint(img, (10, 10, 20, 20), 0x0AA008)
    assert vision.any_match(img[10:21, 10:21], 0x0AA008, 0)
    assert vision.any_match(img[10:21, 10:21], 0x0DA30B, 3)
    assert not vision.any_match(img[10:21, 10:21], 0x0DA30B, 2)

def test_probe_inverted_corners():
    p = atlas.Probe(450, 410, 380, 490, atlas.RED_DOT, 32)
    assert p.rect == (380, 410, 450, 490)

def test_green_boxes_two_side_by_side():
    img = blank(); paint(img, (100, 100, 300, 160), 0x0AA008); paint(img, (400, 100, 600, 160), 0x0AA008)
    boxes = vision.green_boxes(img[0:200, 0:700], origin=(0, 0))
    assert len(boxes) == 2 and boxes[0][0] == 100 and boxes[1][0] == 400

def test_gem_share_purple_vs_green():
    g = blank()[0:10, 0:10].copy(); paint(g, (0, 0, 9, 9), 0x0AA008)
    p = blank()[0:10, 0:10].copy(); paint(p, (0, 0, 9, 9), 0xC040E0)
    assert vision.gem_share(g) == 0.0 and vision.gem_share(p) == 1.0
```

- [ ] **Step 3: Run** `uv run pytest tests/test_vision.py -v`. Expected: FAIL, modules missing.

- [ ] **Step 4: Implement** `atlas.py` (dataclasses, colour constants, REF values only; feature constants come in later tasks) and `vision.py`. Port `match_mask` and `green_boxes` from the snapshot's `vision__probes.py` / `vision__buttons.py`, dropping the `g`/anchor parameters: `green_boxes` takes the image and the logical origin of that image. `conftest.py` provides `blank`/`paint`.

- [ ] **Step 5: Run** `uv run pytest tests/test_vision.py -v`. Expected: 4 passed.

---

### Task 2: Settings

**Files:**
- Create: `firestone_clicker/config.py`, `settings.toml`, `tests/test_config.py`

**Interfaces:**
- Produces: `config.Config` dataclass with `delay_s:int=60`, `features: dict[str,bool]` (keys `expeditions, awaken, ptree, map_missions, alchemist, research, heroes, guardian`, all True), `alchemist: dict[str,bool]` (`dragon_blood, strange_dust, exotic_coins`), `heroes: dict[str,bool]` (`h1..h5, guardian, special`), `guardian_evolve:bool=True`, `guardian_train:bool=True`, `guardian_train_target:int=1`, `ptree: dict[str,bool]` (20 node names from `PTREE_NODES`, all True). `config.load(path: Path) -> Config`: missing file returns defaults; present keys override.

- [ ] **Step 1: Write failing tests**:

```python
def test_defaults_when_missing(tmp_path):
    c = config.load(tmp_path / "nope.toml")
    assert c.delay_s == 60 and all(c.features.values()) and c.guardian_train_target == 1

def test_override(tmp_path):
    (tmp_path / "s.toml").write_text('delay_s = 5\n[features]\nresearch = false\n[guardian]\ntrain_target = 3\n')
    c = config.load(tmp_path / "s.toml")
    assert c.delay_s == 5 and c.features["research"] is False and c.guardian_train_target == 3

def test_rejects_bad_train_target(tmp_path):
    (tmp_path / "s.toml").write_text('[guardian]\ntrain_target = 7\n')
    with pytest.raises(ValueError): config.load(tmp_path / "s.toml")
```

- [ ] **Step 2: Run** `uv run pytest tests/test_config.py -v`. Expected: FAIL.
- [ ] **Step 3: Implement** `config.py` with `tomllib`. Write `settings.toml` at the repo root containing every key with its default and a one-line comment per section.
- [ ] **Step 4: Run** tests. Expected: 3 passed.

---

### Task 3: Windows context: window, capture, input, stop event

**Files:**
- Create: `firestone_clicker/ctx.py`, `firestone_clicker/win.py`, `tests/test_ctx.py`, `tools/smoke.py`

**Interfaces:**
- Produces: `ctx.Ctx` protocol-like base with methods `grab(rect) -> np.ndarray` (logical inclusive rect → BGRA), `move(x,y)`, `click(x,y)`, `key(name:str)`, `key_hold(name:str, ms:int)`, `sleep(ms:float)` (raises `ctx.Stopped` if the stop event is set; polls every 100 ms), `log(msg:str)`, `stop: threading.Event`, `dry_run: bool`. `ctx.LiveCtx(dry_run=False)` implements it with mss (one instance, main thread only) and pynput; in dry_run, `move/click/key/key_hold` only log.
- Produces: `win.find_client_rect() -> tuple[int,int,int,int] | None` (screen x, y, w, h of the largest visible window of process `Firestone.exe`), `win.activate(hwnd)`, `win.check_client(rect) -> None` raising `win.BadWindow` unless `w == 1920 and 1000 <= h <= 1040`. `LiveCtx.offset` = client origin minus `REF_ORIGIN`, applied inside `grab/move/click`.
- Produces: `ctx.FakeCtx(screens: list[np.ndarray])` for tests: `grab` slices the current screen; each `click` appends `(x,y)` to `.clicks` and advances to the next screen if one remains; `key` appends to `.keys`; `sleep` records ms and returns immediately; `log` appends to `.logs`.
- Produces: `ctx.install_hotkey(stop: threading.Event)` for Win+Esc via pynput listener.

- [ ] **Step 1: Write failing tests** (FakeCtx and pure logic only; no live window in tests):

```python
def test_fake_ctx_advances_on_click():
    a, b = blank(), blank(); paint(b, (0, 0, 5, 5), 0xFF0000)
    c = FakeCtx([a, b]); assert not vision.any_match(c.grab((0,0,5,5)), 0xFF0000, 0)
    c.click(1, 1); assert vision.any_match(c.grab((0,0,5,5)), 0xFF0000, 0)

def test_sleep_aborts_on_stop():
    c = LiveCtx(dry_run=True); c.stop.set()
    with pytest.raises(Stopped): c.sleep(20000)

def test_client_rect_rejects_wrong_size():
    with pytest.raises(win.BadWindow): win.check_client((0, 31, 1600, 900))
    win.check_client((0, 31, 1920, 1009))
```

- [ ] **Step 2: Run** `uv run pytest tests/test_ctx.py -v`. Expected: FAIL.
- [ ] **Step 3: Implement** `win.py` with ctypes user32 + psutil (port `find_game_window`/`activate` logic from the infra report: EnumWindows over PIDs named Firestone.exe, largest client area, `SetForegroundWindow` with `AttachThreadInput` fallback; call `SetProcessDpiAwarenessContext(-4)` at import). Implement `ctx.py`. `LiveCtx.sleep` loops `stop.wait(0.1)` until elapsed.
- [ ] **Step 4: Run** tests. Expected: 3 passed.
- [ ] **Step 5: Write `tools/smoke.py`**: find window, print client rect and offset, `check_client`, save a full client capture to `diag/smoke.png` (via `mss.tools.to_png`), move the mouse to logical `(1851, 84)` without clicking. Run `uv run python tools/smoke.py` with the game open. Expected: prints `client=(0, 31, 1920, 1009)` or similar, writes the PNG, pointer lands on the settings gear.

---

### Task 4: Navigation primitives

**Files:**
- Create: `firestone_clicker/nav.py`, `tests/test_nav.py`
- Modify: `firestone_clicker/atlas.py` (add nav constants)

**Interfaces:**
- Atlas adds: `BIG_CLOSE=Point(1851,84)`, `SETTINGS_CLOSE=Point(1725,116)`, `MM_SETTINGS_OPEN=Probe(1542,655,1654,687,0x285483,3)`, `DIALOG_CLOSE_X=Probe(1849,81,1858,90,0xFFF9CE,30)`, `TOWN_OPEN=Probe(35,447,65,465,0xF6C100,12)`.
- Produces in `nav.py`: `found(ctx, probe) -> bool`; `wait_for(ctx, probe, timeout_ms=6000) -> bool` (two hits 100 ms apart); `click(ctx, p: Point, settle_ms=1500)` (move, sleep 150, click, sleep settle); `safe_click(ctx, p, rect, settle_ms=1500) -> bool` (False and a log line `gem: skipped <x,y>` when `gem_share(grab(rect)) > GEM_MAX=0.004`); `big_close(ctx)`; `open_town(ctx) -> bool` (key `t`, wait_for TOWN_OPEN); `require_screen(ctx, p, expect=DIALOG_CLOSE_X, via_town=False) -> bool`; `find_dialog_x(ctx, band) -> Point|None` (orange ring ≥40 px holding cream cross; use `green_boxes`-style projection on `match_mask(DIALOG_RING, 30)` and confirm `DIALOG_X_CROSS` inside); `go_home(ctx) -> bool` (loop: if MM_SETTINGS_OPEN → click SETTINGS_CLOSE, return True; else click BIG_CLOSE; a click that changes <30% of a 32x18 thumbnail's cells by mean ≥40 is a stall; stop after 3 stalls or 10 clicks → False). `thumbnail(img) -> np.ndarray` and `changed(a, b) -> bool` live here too.

- [ ] **Step 1: Write failing tests**:

```python
def test_go_home_detects_settings_and_closes():
    s0 = blank(); s1 = blank(); paint(s1, atlas.MM_SETTINGS_OPEN.rect, 0x285483)
    c = FakeCtx([s0, s1]); assert nav.go_home(c) is True
    assert c.clicks == [(1851, 84), (1725, 116)]

def test_go_home_gives_up():
    c = FakeCtx([blank()]); assert nav.go_home(c) is False
    assert len(c.clicks) <= 10

def test_safe_click_skips_gem():
    s = blank(); paint(s, (100, 100, 200, 150), 0x0AA008); paint(s, (150, 110, 170, 130), 0xC040E0)
    c = FakeCtx([s]); assert nav.safe_click(c, atlas.Point(150, 125), (100, 100, 200, 150)) is False
    assert c.clicks == []

def test_safe_click_clicks_when_clean():
    s = blank(); paint(s, (100, 100, 200, 150), 0x0AA008)
    c = FakeCtx([s]); assert nav.safe_click(c, atlas.Point(150, 125), (100, 100, 200, 150)) is True

def test_wait_for_needs_two_hits():
    s = blank(); paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    assert nav.wait_for(FakeCtx([s]), atlas.TOWN_OPEN) is True
    assert nav.wait_for(FakeCtx([blank()]), atlas.TOWN_OPEN, timeout_ms=300) is False
```

- [ ] **Step 2: Run** `uv run pytest tests/test_nav.py -v`. Expected: FAIL.
- [ ] **Step 3: Implement** `nav.py` and the atlas additions.
- [ ] **Step 4: Run** tests. Expected: 5 passed.
- [ ] **Step 5: Live check.** Write `tools/probe_check.py`: iterates every `Probe` in `atlas` (via `vars(atlas)` plus nested tuples), prints `name: FOUND/missing`, and saves `diag/probe_check.png` with every `Point` drawn as a red cross and every probe rect outlined. Run it on the main screen, then run `uv run python -c "from firestone_clicker import ctx, nav; c=ctx.LiveCtx(); print(nav.go_home(c))"` from a dialog you opened by hand. Expected: `True`, game back on the main screen.

---

### Task 5: Heroes

**Files:**
- Create: `firestone_clicker/features/__init__.py`, `firestone_clicker/features/heroes.py`, `tests/test_heroes.py`
- Modify: `atlas.py`

**Interfaces:**
- Atlas adds `HERO_UPGRADE_SLOTS` verbatim from snapshot line 1212 (7 entries of `(setting, probe_rect, Point)`), with settings renamed to config keys: `UpgradeSpecial→special, UpgradeH5→h5 … UpgradeGuardian→guardian`.
- Produces: `heroes.run(ctx, cfg: Config) -> None`.

- [ ] **Step 1: Write failing tests**:

```python
def test_heroes_clicks_enabled_green_slots():
    s = blank(); paint(s, (1862, 434, 1888, 469), 0x0AA008)   # H1 ready
    c = FakeCtx([s, s]); heroes.run(c, Config())
    assert c.keys[0] == "u" and (1670, 427) in c.clicks and (1851, 84) == c.clicks[-1]

def test_heroes_skips_disabled():
    s = blank(); paint(s, (1862, 434, 1888, 469), 0x0AA008)
    cfg = Config(); cfg.heroes["h1"] = False
    c = FakeCtx([s, s]); heroes.run(c, cfg); assert (1670, 427) not in c.clicks

def test_heroes_skips_paid():
    s = blank(); paint(s, (1862, 434, 1888, 469), 0x0AA008); paint(s, (1600, 415, 1740, 440), 0xC040E0)
    c = FakeCtx([s, s]); heroes.run(c, Config()); assert (1670, 427) not in c.clicks
```

- [ ] **Step 2: Run** `uv run pytest tests/test_heroes.py -v`. Expected: FAIL.
- [ ] **Step 3: Implement** `heroes.run`: `ctx.key("u")`, sleep 1500, for each slot: if enabled and `any_match(grab(rect), GREEN_BUTTON, 3)` → `safe_click(ctx, point, gem_rect)` where `gem_rect = (px-100, py-25, px+100, py+25)`; then `big_close`.
- [ ] **Step 4: Run** tests. Expected: 3 passed.
- [ ] **Step 5: Live:** `uv run python -m firestone_clicker --once heroes --dry-run` (main loop CLI lands in Task 11; until then use `uv run python -c "...heroes.run(ctx.LiveCtx(dry_run=True), config.load(Path('settings.toml')))"`). Expected: log shows the U key, probe hits that match what you see, no clicks. Then live once and watch.

---

### Task 6: Guild screen: expeditions, awaken, personal tree

**Files:**
- Create: `features/guild.py`, `tests/test_guild.py`
- Modify: `atlas.py`

**Interfaces:**
- Atlas adds: `MAIN_GUILD_ICON=Point(1857,481)`, `GUILD_EXPEDITION_DOT=Probe(450,410,380,490,RED_DOT,RED_DOT_VAR)`, `GUILD_EXPEDITIONS=Point(308,406)`, `GUILD_EXPEDITION_START=Point(1321,331)`, `GUILD_PTREE_ENTRY=Point(1560,366)`, `AWAKEN_*` (DOT, OPEN, X1, BUTTON_ORANGE, BUTTON_GREEN, BUTTON, AUTO_READY, AUTO, MULTIPLIERS) verbatim from snapshot lines 916–933, `PTREE_OPEN/CONFIRM/UPGRADE/NODES` verbatim from lines 969–992.
- Produces: `guild.run(ctx, cfg)` which does one guild visit: `require_screen(MAIN_GUILD_ICON)`, then `expeditions(ctx)` if enabled, `awaken(ctx)` if enabled, `ptree(ctx, cfg)` if enabled, each ending with `big_close` back to the guild screen; finally `big_close`. The three sub-functions are module-level and take `ctx` (and `cfg` for ptree).

- [ ] **Step 1: Write failing tests**:

```python
def test_expeditions_claims_and_starts_on_dot():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE); paint(s, atlas.GUILD_EXPEDITION_DOT.rect, 0xF41000)
    c = FakeCtx([s]*6); guild.expeditions(c)
    assert c.clicks.count((1321, 331)) == 2

def test_expeditions_noop_without_dot():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE)
    c = FakeCtx([s]); guild.expeditions(c); assert (308, 406) not in c.clicks

def test_awaken_walks_multipliers_then_auto():
    s = blank(); paint(s, atlas.AWAKEN_DOT.rect, 0xF41000); paint(s, atlas.AWAKEN_BUTTON_ORANGE.rect, 0xF4A044)
    paint(s, (1727, 632, 1815, 692), 0x0A9F05)                       # x80 available
    s2 = s.copy(); paint(s2, atlas.AWAKEN_AUTO_READY.rect, 0x0A9F05)
    c = FakeCtx([s, s, s, s2, s2, s2]); guild.awaken(c)
    assert (1772, 666) in c.clicks and (1774, 993) in c.clicks

def test_awaken_green_single():
    s = blank(); paint(s, atlas.AWAKEN_DOT.rect, 0xF41000); paint(s, atlas.AWAKEN_BUTTON_GREEN.rect, 0x0A9F05)
    c = FakeCtx([s]*4); guild.awaken(c); assert (1725, 582) in c.clicks

def test_ptree_only_enabled_nodes_and_gem_gate():
    cfg = Config(); [cfg.ptree.__setitem__(k, False) for k in cfg.ptree]; cfg.ptree["AttDmg"] = True
    s = blank(); paint(s, (1660, 536, 1860, 586), 0xC040E0)           # upgrade button carries a gem
    c = FakeCtx([s]*10); guild.ptree(c, cfg)
    assert (365, 313) in c.clicks and (1760, 561) not in c.clicks
```

- [ ] **Step 2: Run** `uv run pytest tests/test_guild.py -v`. Expected: FAIL.
- [ ] **Step 3: Implement** per spec. Gem rects: expedition start `(1221,306,1421,356)`, awaken buttons `(1600,566,1845,612)` and auto `(1650,955,1900,1015)`, multipliers their own probe rect, ptree confirm `(860,655,1060,705)` and upgrade `(1660,536,1860,586)`. Awaken auto settle 20000, awaken button settle 3000, multiplier taps settle 1000. Expedition: after the two start clicks, sleep 1000, big_close, re-check dot twice 500 ms apart, one more start if still there.
- [ ] **Step 4: Run** tests. Expected: 5 passed.
- [ ] **Step 5: Live:** run `guild.run` in dry-run on the guild screen, compare logged probe results to the screen; then live once. Adjust the gem rects from `diag/` captures if a button sits elsewhere.

---

### Task 7: Guardian

**Files:**
- Create: `features/guardian.py`, `tests/test_guardian.py`
- Modify: `atlas.py`

**Interfaces:**
- Atlas adds: `TOWN_MAGIC_QUARTER=Point(658,284)`, `GUARDIAN_EVOLVE_DOT=Probe(1307,107,1346,136,RED_DOT,RED_DOT_VAR)`, `GUARDIAN_EVOLVE_TAB=Point(1200,165)`, `GUARDIAN_EVOLVE_BUTTON=Point(1117,750)`, `GUARDIAN_BACK_TAB=Point(1049,171)`, `GUARDIAN_TRAIN_READY=Probe(1199,766,1257,810,GREEN_BUTTON,3)`, `GUARDIAN_TRAIN_BUTTON=Point(1138,787)`.
- Produces: `guardian.run(ctx, cfg)`.

- [ ] **Step 1: Write failing tests**:

```python
def test_guardian_evolve_and_train():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE); paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    paint(s, atlas.GUARDIAN_EVOLVE_DOT.rect, 0xF41000); paint(s, atlas.GUARDIAN_TRAIN_READY.rect, 0x0AA008)
    cfg = Config(); cfg.guardian_train_target = 3
    c = FakeCtx([s]*10); guardian.run(c, cfg)
    assert (1117, 750) in c.clicks and (1138, 787) in c.clicks
    assert c.keys.count("right") == 2 and ("left", 2000) in c.key_holds

def test_guardian_train_skips_paid():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE); paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    paint(s, atlas.GUARDIAN_TRAIN_READY.rect, 0x0AA008); paint(s, (1100, 775, 1120, 800), 0xC040E0)
    c = FakeCtx([s]*10); guardian.run(c, Config()); assert (1138, 787) not in c.clicks
```

- [ ] **Step 2: Run** tests. Expected: FAIL.
- [ ] **Step 3: Implement** per spec: `require_screen(TOWN_MAGIC_QUARTER, via_town=True)`, sleep 1000; evolve branch with settle 10500 on the evolve button (gem rect `(1017,725,1217,775)`), `key_hold("left", 2000)`, `key("right")` ×(target−1) with 100 ms sleeps, train `safe_click` gem rect `(1038,762,1238,812)`; `big_close`. `FakeCtx.key_holds` records `(name, ms)`.
- [ ] **Step 4: Run** tests. Expected: 2 passed.
- [ ] **Step 5: Live** dry-run then live on the Magic Quarter.

---

### Task 8: Alchemist

**Files:**
- Create: `features/alchemist.py`, `tests/test_alchemist.py`
- Modify: `atlas.py`

**Interfaces:**
- Atlas adds: `TOWN_ALCHEMIST=Point(511,837)`, `AlchemySlot` dataclass and `ALCHEMY_SLOTS` verbatim from snapshot lines 705–748 (slot `.key` field added: `dragon_blood`, `strange_dust`, `exotic_coins`), `ALCHEMY_BUTTON_ORANGE_MIN=0.15`, `ALCHEMY_GEM_MAX=60/12950`.
- Produces: `alchemist.run(ctx, cfg)`; `alchemist.classify(img) -> Literal["other","free","paid"]`.

- [ ] **Step 1: Write failing tests**:

```python
def test_classify():
    other = blank()[0:70, 0:185].copy()
    free = other.copy(); paint(free, (0, 0, 184, 69), 0xF9AA47)
    paid = free.copy(); paint(paid, (80, 20, 100, 40), 0xC040E0)
    assert alchemist.classify(other) == "other" and alchemist.classify(free) == "free" and alchemist.classify(paid) == "paid"

def test_collects_done_and_starts_idle():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE); paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    blood, dust, coin = atlas.ALCHEMY_SLOTS
    paint(s, blood.complete.rect, 0x0AA008)                      # blood done → collect
    # dust: nothing painted → "other", not running → start
    paint(s, coin.in_progress.rect, 0x916A38)                    # coin running → leave
    c = FakeCtx([s]*12); alchemist.run(c, Config())
    assert (949, 777) in c.clicks and (1286, 786) in c.clicks and (1641, 767) not in c.clicks

def test_never_clicks_paid():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE); paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    blood = atlas.ALCHEMY_SLOTS[0]; paint(s, blood.button, 0xF9AA47); paint(s, (900, 780, 930, 800), 0xC040E0)
    c = FakeCtx([s]*12); alchemist.run(c, Config()); assert (949, 777) not in c.clicks and (951, 771) not in c.clicks
```

- [ ] **Step 2: Run** tests. Expected: FAIL.
- [ ] **Step 3: Implement** per spec, porting the flow from `features__alchemist.py` (drop the `AlchCollect` setting: always collect). Park at `TOWN_ALCHEMIST` before every read. `classify`: `color_share(img, ORANGE_1, 40) < 0.15 → other`; else `gem_share(img) > ALCHEMY_GEM_MAX → paid` else `free`.
- [ ] **Step 4: Run** tests. Expected: 3 passed.
- [ ] **Step 5: Live** dry-run then live at the alchemist. Tune `ALCHEMY_GEM_MAX` from a `diag/` capture of a paid button if the share is off.

---

### Task 9: Research (minimal)

**Files:**
- Create: `features/research.py`, `tests/test_research.py`
- Modify: `atlas.py`

**Interfaces:**
- Atlas adds: `TOWN_LIBRARY=Point(329,657)`, `RS_FIRESTONE_TREE=Point(1816,610)`, `RS_PARK=Point(1300,60)`, `RS_SLOT_STRIP=(60,880,1450,1010)`, `RS_SLOT_DONE_VAR=25`, `RS_BUTTON_MIN_W=40`, `RS_BUTTON_MIN_H=25`, `RS_TREE_AREA=(40,110,1725,860)`, `RS_AVAILABLE=0x1D49DE`, `RS_AVAILABLE_VAR=32`, `RS_BOX_MIN_W=140`, `RS_BOX_MIN_H=60`, `RS_POPUP_BUTTON_BAND=(620,630,980,860)`, `RS_POPUP_BUTTON_MIN_W=200`, `RS_POPUP_X_BAND=(1170,160,1300,340)`, `RS_POPUP_CLOSE_X=Probe(1215,200,1263,248,DIALOG_RING,30)`, `RS_POPUP_CLOSE=Point(1239,224)`, `RS_POPUP_OUTSIDE=Point(100,150)`, `RS_SLOTS_FULL_X=Probe(1346,331,1394,379,DIALOG_RING,30)`, `RS_SLOTS_FULL_CREAM=Probe(1090,641,1110,661,0xE8D1B7,25)`, `RS_SLOTS_FULL_CLOSE=Point(1370,355)`, `RS_MAX_STARTS=2`.
- Produces: `research.run(ctx, cfg)`; `research.available_boxes(img, origin) -> list[rect]` (generalise `vision.green_boxes` into `vision.color_boxes(img, origin, color, var, min_w, min_h)` and make `green_boxes` call it).

- [ ] **Step 1: Write failing tests**:

```python
def test_claims_done_slot():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE); paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    paint(s, (600, 930, 760, 990), 0x0AA008)                          # done button in left slot
    c = FakeCtx([s]*10); research.run(c, Config())
    assert any(600 <= x <= 760 and 930 <= y <= 990 for x, y in c.clicks)

def test_starts_available_box_free_only():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE); paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    paint(s, (225, 224, 608, 325), 0x0D49DE)                          # available box
    popup = s.copy(); paint(popup, (650, 680, 942, 740), 0x0AA008)     # green Research button
    paid = popup.copy(); paint(paid, (700, 700, 720, 720), 0xC040E0)
    c = FakeCtx([s, s, popup, popup, popup, popup]); research.run(c, Config())
    assert any(650 <= x <= 942 and 680 <= y <= 740 for x, y in c.clicks)
    c2 = FakeCtx([s, s, paid, paid, paid, paid]); research.run(c2, Config())
    assert not any(650 <= x <= 942 and 680 <= y <= 740 for x, y in c2.clicks)

def test_slots_full_closed():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE); paint(s, atlas.TOWN_OPEN.rect, 0xF6C100)
    paint(s, atlas.RS_SLOTS_FULL_X.rect, 0xFF6109); paint(s, atlas.RS_SLOTS_FULL_CREAM.rect, 0xE8D1B7)
    c = FakeCtx([s]*10); research.run(c, Config()); assert (1370, 355) in c.clicks
```

- [ ] **Step 2: Run** tests. Expected: FAIL.
- [ ] **Step 3: Implement** per spec: enter library, click Firestone tree, park; claim every green box in `RS_SLOT_STRIP` (settle 1500); then up to `RS_MAX_STARTS` times: if slots-full dialog → close and stop; find the first available box in `RS_TREE_AREA`, click its centre (settle 800), wait up to 2000 ms for a green box ≥200 wide in `RS_POPUP_BUTTON_BAND`; `safe_click` it with its own rect; else close via `find_dialog_x(RS_POPUP_X_BAND)` → `RS_POPUP_CLOSE_X` → `RS_POPUP_OUTSIDE`. `big_close`.
- [ ] **Step 4: Run** tests. Expected: 3 passed.
- [ ] **Step 5: Live** dry-run in the library; confirm the blue value on Windows (`0x0D49DE`) sits inside `RS_AVAILABLE ± 32`; then live once.

---

### Task 10: Map missions (minimal)

**Files:**
- Create: `features/map_missions.py`, `tests/test_map.py`
- Modify: `atlas.py`

**Interfaces:**
- Atlas adds: `MR_FREE_RESET=Probe(221,878,277,891,ORANGE_2,3)`, `MR_FREE_RESET_BUTTON=Point(173,918)`, `MR_REFRESH_RECT=(95,869,297,976)`, `MR_NO_MISSIONS=Probe(117,249,208,334,0x1452B4,3)`, `MR_MISSION_DONE=Probe(207,305,244,348,GREEN_BUTTON,3)`, `MR_FIRST_MISSION=Point(162,334)`, `MAP_TROOP_IDLE=Probe(1175,996,1187,1012,IDLE_TROOP,10)`, `MAP_SPOTS: tuple[Point,...]` = every `(x,y)` from the snapshot's `MAP_MISSION_GROUPS` (lines 1476–~1560, all groups in order) with `y >= 100`, `MAP_POPUP_BAND=(300,150,1620,900)`, `MAP_MAX_COLLECT=10`.
- Produces: `map_missions.run(ctx, cfg)`; `map_missions.close_popup(ctx) -> bool` (dialog X in `MAP_POPUP_BAND`, else tap `(1700, 540)`).

- [ ] **Step 1: Write failing tests**:

```python
def test_collect_loop_bounded():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE); paint(s, atlas.MR_MISSION_DONE.rect, 0x0AA008)
    c = FakeCtx([s]*40); map_missions.run(c, Config())
    assert c.clicks.count((162, 334)) == 10 and c.keys[0] == "m"

def test_starts_free_mission_only():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE); paint(s, atlas.MR_NO_MISSIONS.rect, 0x1452B4)
    paint(s, atlas.MAP_TROOP_IDLE.rect, 0x542710)
    popup = s.copy(); paint(popup, (700, 700, 940, 760), 0x0AA008)
    paid = popup.copy(); paint(paid, (720, 720, 740, 740), 0xC040E0)
    c = FakeCtx([s, s, popup] + [s]*80); map_missions.run(c, Config())
    assert any(700 <= x <= 940 and 700 <= y <= 760 for x, y in c.clicks)
    c2 = FakeCtx([s, s, paid] + [s]*80); map_missions.run(c2, Config())
    assert not any(700 <= x <= 940 and 700 <= y <= 760 for x, y in c2.clicks)

def test_stops_when_no_idle_troop():
    s = blank(); paint(s, atlas.DIALOG_CLOSE_X.rect, 0xFFF9CE); paint(s, atlas.MR_NO_MISSIONS.rect, 0x1452B4)
    c = FakeCtx([s]*5); map_missions.run(c, Config())
    assert all(p not in c.clicks for p in [(pt.x, pt.y) for pt in atlas.MAP_SPOTS])
```

- [ ] **Step 2: Run** tests. Expected: FAIL.
- [ ] **Step 3: Implement** per spec: `key("m")`, `wait_for(DIALOG_CLOSE_X)`; free refresh if `MR_FREE_RESET` and `gem_share(grab(MR_REFRESH_RECT)) <= GEM_MAX`; collect loop while `MR_MISSION_DONE` and not `MR_NO_MISSIONS`, max 10, each: click first mission, sleep 1000, click the first green box ≥100 wide in `MAP_POPUP_BAND` (Okay) via `safe_click`, else `close_popup`; start pass: for each `MAP_SPOTS` while `MAP_TROOP_IDLE`: click spot (settle 1000), green box in band → `safe_click`, else `close_popup`; then `go_home`.
- [ ] **Step 4: Run** tests. Expected: 3 passed.
- [ ] **Step 5: Live:** with the map at its default position, dry-run and compare which spots land on missions in `diag/probe_check.png`. Remove spots that hit nothing on the user's map. Then live once.

---

### Task 11: Main loop and CLI

**Files:**
- Create: `firestone_clicker/__main__.py`, `firestone_clicker/loop.py`, `tests/test_loop.py`

**Interfaces:**
- Produces: `loop.FEATURES: list[tuple[str, Callable[[Ctx, Config], None]]]` in order `heroes, guild, guardian, alchemist, research, map_missions` (config keys `expeditions/awaken/ptree` gate inside `guild.run`; `guild` runs if any of the three is on). `loop.run_cycle(ctx, cfg, only: str|None=None) -> bool` (False when `go_home` failed after the cycle). `loop.main(ctx, cfg, once: str|None, max_home_failures=3)`.
- CLI: `python -m firestone_clicker [--dry-run] [--once FEATURE] [--settings PATH]`. Logs to stdout and `bot.log`. On any feature exception: log traceback, save `diag/<feature>-<timestamp>.png`, `go_home`. Exits on `Stopped`, on `win.BadWindow`, when the window is gone, or after 3 consecutive `go_home` failures.

- [ ] **Step 1: Write failing tests**:

```python
def test_run_cycle_runs_enabled_only(monkeypatch):
    calls = []
    monkeypatch.setattr(loop, "FEATURES", [("a", lambda c, f: calls.append("a")), ("b", lambda c, f: calls.append("b"))])
    cfg = Config(); cfg.features.update({"a": True, "b": False})
    loop.run_cycle(FakeCtx([blank()]*5), cfg); assert calls == ["a"]

def test_feature_exception_is_contained(monkeypatch):
    def boom(c, f): raise RuntimeError("x")
    monkeypatch.setattr(loop, "FEATURES", [("a", boom)])
    cfg = Config(); cfg.features["a"] = True
    loop.run_cycle(FakeCtx([blank()]*20), cfg)   # must not raise

def test_loop_exits_after_three_home_failures(monkeypatch):
    monkeypatch.setattr(loop, "FEATURES", [])
    cfg = Config(); cfg.delay_s = 0
    c = FakeCtx([blank()]*200)
    loop.main(c, cfg, once=None); assert c.logs[-1].startswith("exit: go_home failed 3")
```

- [ ] **Step 2: Run** tests. Expected: FAIL.
- [ ] **Step 3: Implement** `loop.py` and `__main__.py` (argparse, `install_hotkey`, `find_client_rect`/`check_client`/`activate` at start and at each cycle start, `LiveCtx`).
- [ ] **Step 4: Run** `uv run pytest -v`. Expected: all tests pass.
- [ ] **Step 5: Live:** `uv run python -m firestone_clicker --dry-run` for one cycle; then `uv run python -m firestone_clicker` observed by the user for a full cycle; then a 1 hour unattended run. Check `bot.log` for `gem: skipped` lines, stalls, and `diag/` captures.
- [ ] **Step 6: Cleanup:** delete `C:\Users\Adnan\fsb_src\` (ask the user first).

---

## Self-review notes

- Spec coverage: every feature, the gem gate, go_home exit rule, delay semantics, dry-run and `--once`, probe_check script, and verification steps have a task. Crash relaunch, scaling, GUI are non-goals and absent.
- Type consistency: `Ctx` methods (`grab, move, click, key, key_hold, sleep, log, stop, dry_run`), `FakeCtx` fields (`clicks, keys, key_holds, logs`), `nav` function names, `Config` field names are used identically across tasks.
- Proportion: plan is shorter than the expected code; bodies appear only for tests.
