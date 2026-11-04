# Firestone Clicker: design

Date: 2026-11-04

## Intent

A small Windows-only Python bot that keeps Firestone Idle RPG (Epic build) progressing while the user is away. It replaces Lutakh/firestone-bot (python-rework branch), which does the job but carries ~20 features, a GUI, macOS support, OCR, template matching and an updater. The user wants only seven actions, run in a loop, with no UI.

Reference bot: https://github.com/Lutakh/firestone-bot (MIT), branch `python-rework`, commit `fba1b7fd92b7ab57f0dfcfa56f8089f6199fddbf`. A local snapshot of its source is at `C:\Users\Adnan\fsb_src\`; tables marked "verbatim from source" below (AlchemySlot, HERO_UPGRADE_SLOTS, PTREE_NODES, MAP_MISSION_GROUPS, AWAKEN_MULTIPLIERS) are copied from `firestone_bot/vision/atlas.py` there. None have been verified on the user's machine yet; verification is the first implementation step.

## Goals

- Run unattended on the user's PC: dedicated machine, bot owns mouse and keyboard.
- Automate exactly: guild expeditions, world-map missions, alchemist, research, hero upgrades, guardian evolve/train, hero awakening, personal tree.
- Settings in one plain file. Everything on by default.
- Minimal code and deps. Target under ~800 lines total.

## Non-goals

- No GUI, no updater, no macOS/Linux, no Steam-specific handling.
- No crash relaunch. If the game window is gone, log and exit.
- No OCR, no template/icon matching, no map alignment, no research priorities.
- No pause-on-user-input guard. Win+Esc stops the bot.
- No account-level gating. Account is 200+, in a guild, everything unlocked.

## Anti-goals (would make this a failure)

- Clicking an orange "pay gems" button. Every spend path must probe for the gem and abort.
- Getting stuck on a popup forever. Every feature must bail to the go-home routine after a bounded number of closes.
- Drifting the world map. The bot never drags, zooms or scrolls the map.

## Constraints

- Windows 11, Epic build, 1920x1080 monitor, 100% DPI, game windowed and maximized, English. Client rect is 1920x1009 at y=31. Coordinates are absolute screen pixels for this setup only. No scaling support.
- Python 3.12, `uv` for env. Deps: `mss`, `numpy`, `pynput`, `psutil`. Nothing else.
- Game must already be running when the bot starts.

## Architecture

Single package `firestone_clicker/` with flat modules. No classes beyond small dataclasses.

```
firestone_clicker/
  __main__.py     # loop: for each enabled feature: run, go_home; sleep delay
  config.py       # load settings.toml, dataclass with defaults
  win.py          # find window by process name Firestone.exe, activate, client rect
  screen.py       # mss grab(rect) -> numpy BGRA; probe(Probe) -> bool; thumbnail diff
  input.py        # click(Point), key(k), key_hold(k, ms), move(Point), Win+Esc listener
  atlas.py        # Point / Probe dataclasses and every constant, grouped by feature
  nav.py          # go_home(), open_town(), big_close(), require_screen()
  features/
    expeditions.py
    map_missions.py
    alchemist.py
    research.py
    heroes.py
    guardian.py
    awaken.py
    ptree.py
settings.toml
```

### Core primitives

- `Point(x, y)` and `Probe(x1, y1, x2, y2, color, var)`. Probe passes when any pixel in the inclusive rect has each of R, G, B within `var` of `color`. Capture is BGRA so channel 2 is R. Each probe grabs only its own rect.
- `click(p, settle_ms=1500)`: move, hover 150 ms, click, sleep settle. `found(probe)`. `wait_for(probe, timeout_ms=6000)`: needs two hits 100 ms apart.
- `changed(before)`: coarse thumbnail diff of the client; a close that changes fewer than 30% of cells is a stall.
- `go_home()`: click `BIG_CLOSE=(1851,84)` repeatedly. On the main screen that spot is the settings gear; when settings is detected by `Probe(1542,655,1654,687,0x285483,3)`, click `SETTINGS_CLOSE=(1725,116)` and return True. Give up after 3 stalls or 10 clicks and return False. Also closes the orange-ring X popups (`0xFF6109` ring around `0xFFF9CE` cross) when found.
- `open_town()`: press `t`, wait for `TOWN_OPEN=Probe(35,447,65,465,0xF6C100,12)`.
- `require_screen(point, expect=DIALOG_CLOSE_X, via_town=False)`: optional open_town, click point, wait_for expect. `DIALOG_CLOSE_X=Probe(1849,81,1858,90,0xFFF9CE,30)`.
- Gem check `shows_gem(rect)`: fraction of purple pixels (R and B well above G) in the button rect above a small threshold means paid. Threshold tuned on the user's screen.
- `safe_click(p, rect, settle_ms)`: runs `shows_gem(rect)` on the button's rect first and skips the click (logging it) when a gem shows. Every confirm/start/upgrade button in every feature goes through `safe_click`, including the blind flows (personal tree confirm and upgrade, expedition start, awaken buttons, guardian evolve and train). The user is unsure whether those can become gem spends, so they are gated too. The rect for each is a box around the click point, taken from the live screen during verification.

### Main loop

```
for feature in enabled: 
    try: feature.run()
    except Exception: log, screenshot to diag/, go_home()
    go_home()
sleep(config.delay_s)   # default 60
```
Win+Esc sets a stop event polled every 0.1 s by every sleep. If the game window is not found or not in front at the start of a cycle, log and exit. If `go_home()` returns False three cycles in a row, save a diag screenshot, log, and exit (a popup the closer cannot clear, e.g. reconnect or update notice, is not worth spinning on all night). `delay_s` is a pause between cycles, not a cadence; a full cycle with every feature on takes several minutes.

### Features (minimal flows)

**Expeditions** (guild screen). `require_screen((1857,481))`. If `Probe(380,410,450,490,RED_DOT,32)` (corners normalised from the source): click `(308,406)`, click `(1321,331)` twice (claim then start), sleep 1 s, big_close. Re-check dot after settle; if still there, one more start.

**Awaken** (guild screen, same visit). If `Probe(1107,745,1367,944,RED_DOT,32)`: click `(1192,847)`, click `(1577,400)`. If orange `Probe(1600,566,1845,612,0xF4A044,1)`: walk multipliers highest to lowest (x160 `(1872,666)` … x1 `(1577,400)`, probes per source) until `Probe(1650,955,1900,1015,0x0A9F05,1)`, then click `(1774,993)` settle 20 s. Else if green `Probe(1600,566,1845,612,0x0A9F05,1)`: click `(1725,582)` settle 3 s. big_close.

**Personal tree** (guild screen, same visit, blind). Click `(1560,366)`, click `(1823,945)`. For each enabled node: click node, click `(960,680)`, click `(1760,561)` twice. Nodes: the 20 `PTREE_NODES` from the source. big_close.

**Map missions**. Press `m`, wait_for DIALOG_CLOSE_X. Free refresh: if `Probe(221,878,277,891,0xFCAC47,3)` and no gem in `(95,869,297,976)`: click `(173,918)`. Collect: while not `Probe(117,249,208,334,0x1452B4,3)` and done-probe `Probe(207,305,244,348,0x0AA008,3)`: click `(162,334)`, close popup with Okay/X, max 10. Start: while troop idle `Probe(1175,996,1187,1012,0x542710,10)`: click each of the fixed `MAP_MISSION_GROUPS` spots once (skip y<100 spots, no north drag), sleep 1 s, if a green Start box exists in the popup and no gem: click it; else close popup. One pass. No paid reset. go_home.

**Alchemist**. `require_screen((511,837), via_town=True)`, park pointer at `(511,837)`. For each of the three `AlchemySlot`s (Dragon Blood, Strange Dust, Exotic Coins; probes verbatim from source): if `not_running` found skip; if `complete` found click collect; then classify the button rect: orange share < 0.15 = OTHER, gem share high = PAID, else FREE. FREE: click it. OTHER and not `in_progress`: click start. Never click PAID. big_close.

**Research**. `require_screen((329,657), via_town=True)`, click `(1816,610)` settle 1 s. Park at `(1300,60)`. Claim: find green blobs (`0x0AA008`/`0x16BC15` ±25, min 40x25) in `(60,880,1450,1010)`, click each, settle 1.5 s. Start: find the first dark-blue box (`0x1D49DE` ±32) in `(40,110,1725,860)` without scrolling, click centre, wait up to 2 s, click the left-most green box ≥200 px wide in `(620,630,980,860)` if no gem, else close via `Probe(1215,200,1263,248,0xFF6109,30)` → `(1239,224)` or tap `(100,150)`. Handle "slots full" (`Probe(1346,331,1394,379,0xFF6109,30)` + `Probe(1090,641,1110,661,0xE8D1B7,25)` → click `(1370,355)`). Max 2 starts per visit. big_close.

**Heroes** (classic). Press `u`, sleep 1.5 s. For each enabled slot in `HERO_UPGRADE_SLOTS` (7 entries, verbatim): if `GREEN_BUTTON` ±3 in rect, click point once. big_close. No next-milestone mode.

**Guardian**. `require_screen((658,284), via_town=True)`, sleep 1 s. Evolve: if `Probe(1307,107,1346,136,RED_DOT,32)`: click `(1200,165)`, click `(1117,750)` settle 10.5 s, click `(1049,171)`. Train: if `Probe(1199,766,1257,810,0x0AA008,3)`: hold Left 2 s, press Right (guardian-1) times, click `(1138,787)`. big_close.

Shared colours: `RED_DOT=0xF41000` var 32, `GREEN_BUTTON=0x0AA008`, `GREEN_BUTTON_2=0x16BC15`, `ORANGE_2=0xFCAC47`.

### settings.toml

```toml
delay_s = 60
[features]   # all true by default
expeditions = true
awaken = true
ptree = true
map_missions = true
alchemist = true
research = true
heroes = true
guardian = true
[alchemist]
dragon_blood = true
strange_dust = true
exotic_coins = true
[heroes]
h1 = true ... h5, guardian, special = true
[guardian]
evolve = true
train = true
train_target = 1        # 1 to 4
[ptree]
# 20 node booleans, all true
```

## Implementation order

1. Infra: win, screen, input, atlas skeleton, nav. Verify go_home, open_town, DIALOG_CLOSE_X, TOWN_OPEN on the live game with a `probe_check.py` dev script that prints found/not-found for every probe and marks points on a screenshot.
2. Features in order of cheapness: heroes, expeditions, awaken, ptree, guardian, alchemist, research, map_missions. Each verified live before the next.
3. Loop and settings.

## Verification

- `uv run python -m firestone_clicker --dry-run`: run one cycle with clicks disabled, printing every probe result and intended click.
- `uv run python -m firestone_clicker --once <feature>`: run a single feature live.
- A full live cycle observed by the user, then a 1 hour unattended run with the log checked for stalls and diag screenshots.
- Every probe constant gets checked once by the probe_check script against the user's live screen before being trusted.

## Left to the builder

- Exact gem threshold and orange-share values; tune on live captures.
- Which fixed map spots to keep from `MAP_MISSION_GROUPS` once seen on the user's map.
- Log format (plain text to `bot.log`, one line per action).
