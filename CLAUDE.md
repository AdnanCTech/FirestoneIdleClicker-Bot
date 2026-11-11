# FireStoneClicker

Minimal Windows bot for "Firestone - Idle Clicker Online RPG" (Epic build). Pixel probes + simulated input, no
OCR, no GUI, no relaunch. Replaces the bloated Lutakh/firestone-bot with only what the owner
needs. Design: `docs/superpowers/specs/2026-11-04-firestone-clicker-design.md`. Build plan and
ledger of decisions: `docs/superpowers/plans/2026-11-04-firestone-clicker.md`, `diag/sdd-ledger.md`.

## Repo / release
- Public repo: https://github.com/AdnanCTech/FirestoneIdleClicker-Bot (MIT, credits
  Lutakh/firestone-bot). Repo name differs from the exe name on purpose; leave both.
- Users get `FirestoneClicker-<version>-win64.zip` from Releases (exe + default `settings.toml`
  + README + LICENSE). First release v0.1.0 on 2026-11-04, CI-built zip verified on the live game.
- `.github/workflows/release.yml`: every push runs pytest; a `v*` tag also builds the exe with
  PyInstaller and attaches the zip. Actions are pinned to commit SHAs.
- To release: bump `__version__` in `firestone_clicker/__init__.py`, add a `## X.Y.Z - date`
  section to `CHANGELOG.md` written for players (new / fixed / changed, not a commit list; show
  it to the owner first), commit, `git tag -a vX.Y.Z`, `git push origin main vX.Y.Z`. The
  release job uses that section as the release body and fails if it is missing.
  `.\build.ps1` does the same exe build locally into `dist/`.
- The shipped `settings.toml` is generated from `paths.DEFAULT_SETTINGS` (generic defaults).
  The repo-root `settings.toml` is the owner's personal config and is not shipped.
- `gh` CLI is installed (logged in as AdnanCTech) at `C:\Program Files\GitHub CLI\gh.exe`; it
  may be missing from PATH in a shell started before the install, so call it by full path.
  Use it for runs (`gh run list`), releases (`gh release view/edit`) and repo settings
  (`gh repo edit`) instead of raw API calls.

## Run / test
- `uv run python -m firestone_clicker` loops until Win+Esc or Ctrl+C. `--once <feature>` runs one
  feature, `--dry-run` runs one cycle with input disabled. Logs to terminal and `bot.log`,
  failure captures to `diag/`. Exit code 1 means it gave up (window lost or stuck).
- `uv run pytest -q` (115 tests, ~6 s). Tests paint fake screens; no game needed.
- `uv run python tools/probe_check.py` prints FOUND/missing for every atlas probe on the live
  screen and draws them on `diag/probe_check.png`. `tools/smoke.py` checks window + capture.
- Game must be running. The bot finds `Firestone.exe`, maximizes it and waits until the client
  is 1920x1009 (Unity resizes lazily). Works on a second monitor at negative coordinates.

## Layout
- `atlas.py` every coordinate/colour, grouped per feature, with "measured live" notes.
- `vision.py` numpy matching on BGRA: `match_mask`, `color_boxes` (column projection; merges
  vertically stacked shapes), `blobs` (connected components; use for map icons), `gem_share`,
  `grey_share`.
- `ctx.py` `Ctx` = the side effects (grab, click/move/drag, key, sleep). `LiveCtx` (mss +
  pynput + `win.py`), `FakeCtx` for tests (each click advances to the next scripted screen,
  so fixtures are off-by-one prone: count the opening clicks).
- `nav.py` `found`, `wait_for`, `click`, `safe_click` (gem gate), `go_home`, `open_town`,
  `require_screen`, `find_dialog_x`.
- `features/*.py` one `run(ctx, cfg)` each. `loop.py` cycle order and exit rules.
- `settings.toml` is the only config; `config.py` rejects unknown keys in known sections.
- `schedule.py` runs a feature once per window: `loop.SCHEDULED` maps a feature to its config
  hours, `schedule.window` names the window (latest hour at or before now, crossing midnight),
  `State` keeps finished windows in `state.json` next to the exe (git-ignored). The feature
  returns True when it is done for the window; False retries next cycle. `--once` ignores it.

## Rules learned the hard way
- Logical coords == screen coords only when the client origin is (0,31); `LiveCtx.offset`
  handles the rest. Never hardcode screen coords.
- Every button that could spend anything goes through `nav.safe_click` (gem check on its rect).
  Never click an orange button; grey means unaffordable (alchemist `grey_share`).
- `go_home` clicks only `BIG_CLOSE (1851,84)`; a whole-screen orange-ring search matched the
  Guild market roof and opened it. Dialog-X search is only safe in narrow feature bands.
- Reference-bot coordinates are not trusted until seen live: the personal tree, map and troop
  marker all differed. Check with `probe_check.py`, then a `--once` run, before relying on one.
- Map: every icon is found by the beige pin stand under it (`MAP_ICON_STAND`), not by disc
  colour (wheel and paw discs match the sea and Dreadland). Countdown icons are startable,
  red-winged ones are in progress; the popup decides. Click 35 px above the stand, not 50:
  the higher point sat under a neighbour's animated flags and opened the wrong popup. The
  idle banner's cream gradient matches the stand colour and the banner moves (top seen at y 944
  and 971), so the scan stops at the banner top found on `MAP_BANNER_COLUMN` and a stand cut
  off there still counts. Stands are checked by real pixels (`MAP_ICON_STAND_SHAPE`), not blob
  height: the 4 px cell grid trims the pin's tail to 7 rows in most frames. Scan runs to x 1770: Celenis icons sit at 1720. Mission names by icon: scope Scout, scroll Adventure, sword War,
  paw Monster, dragon Dragon, wheel Naval, volcano Titan (locked, never seen). Monster, Naval
  and Dragon are opened first (`MAP_PRIORITY`, kind from disc colours above the stand). Gated by the idle banner; the map is never dragged. "N/27"
  at the top is idle squads; the bot cannot read "Required squads", so a mission short of
  squads is just closed.
- Personal tree: an out-of-tokens popup puts a green "Get more" under the buy point; it is
  probed (`PTREE_NEED_MORE`) and closed, never blind-clicked.

- Research: columns unlock on levels in the column before (varies, often 8), so the pick is
  the rightmost column with blue boxes, lowest progress bar first (`research.pick_box`, bar
  fill measured from yellow vs dark track pixels; the "15/60" text inflates the ratio a
  little but keeps the order). The tree pans by dragging along y 840 (empty band) and keeps
  its position between opens, so each pass drags to the right end first (view unchanged =
  end), then one column back at a time until a box is found. Never use the arrows next to
  the tree name: they switch trees.
  Two researches run at once at most: `research.running_slots` counts the orange "Speed up"
  buttons in the slot strip and the pass ends when both are busy (checked before every
  start, so the strip is trusted over the slots-full dialog). A grey "Locked" box in view
  (`RS_LOCKED`) stops the drag to the right: everything beyond it is locked too.

- Arena of Kings (`features/arena.py`, town > Battles > right card): three opponents sit
  strongest to weakest left to right and `[arena] opponent` (1 to 3) picks the Fight button by
  position. One visit uses every attempt: Fight, the red battle button (gem-checked), poll
  up to 3 min for the green OK, repeat, hard cap 5. The "N/5" counter is attempts left; at 0/5
  a green "+" replaces the cream panel beside it (`ARENA_HAS_ATTEMPTS` probes the cream) and
  Fight would open a "5 tokens for 1000" offer with a green Confirm that spends arena tokens:
  never press it, the fallback closes it by its X. The arena has its own X at (1800,142); the
  game's x4 battle speed is remembered and not touched. A loss popup has not been seen yet.
  Visited once per `[arena] run_at` window (default 1 and 13 o'clock: attempts reset once a
  day around 9am, two windows give a second chance) via `schedule.py`.

- Free pickaxes (`features/pickaxes.py`, guild > Guild market > Supplies): the market opens on
  a paid real-money bundle tab, so Supplies is clicked first and probed (`PICK_SUPPLIES_OPEN`,
  only meaningful after `PICK_MARKET_OPEN` passed: the dark brown also matches guild art). The
  free card's green Claim is found by `green_boxes` in `PICK_CLAIM_BAND`; grey "Claimed" means
  nothing. The other two cards are orange arena-token buys, never clicked. Pickaxes pile up
  and one Claim takes them all, so it runs once per `[pickaxes] run_at` window (default 1, 13).

- Daily missions (`features/daily_missions.py`, town > Battles > Campaign > "Daily missions"):
  Dungeon has two Fight cards, Liberation a horizontal strip of ~10 Liberate cards (one locked
  behind stars shows no button). A fight starts from its green button, runs ~10 s at the game's
  x4 and ends with a rewards popup whose OK (`nav.wait_green` in `ARENA_OK_BAND`) returns to the
  window. Fought cards read "cleared"/"liberated". The strip keeps its scroll position, so it
  is dragged to the start (y 381, until the view stops changing) then forward one screen at a
  time; a Liberate cut by the window edge is too narrow for `DM_FIGHT_MIN_W`. The Daily popup's
  own "Open" buttons sit in `DM_FIGHT_BAND`, so `DM_WINDOW_X` is re-checked before every fight.
  Once per `[daily_missions] run_at` window. Live 2026-11-11: 2 dungeons + 9 liberations, 108 s.

- Campaign loot (`features/campaign_loot.py`): the "Next loot" chest bottom left of the Campaign
  map fills every 6 h and does not stack. Its Claim is grey while the timer runs (green state
  not yet seen, assumed `GREEN_BUTTON` in `CL_CLAIM_BAND`); the click claims with no popup.
  `[campaign_loot] run_at` defaults to every 6 h and a window is done only once it claimed,
  so the feature retries every cycle inside a window until the chest is ready.

- Engineer tools (`features/engineer.py`, town > Engineer > left card): the "Tools production"
  Claim (`ENG_CLAIM_BAND`) is grey with a countdown while its 6 h timer runs; green unseen,
  assumed `GREEN_BUTTON`. `ENG_OPEN` probes the effects panel's beige at the far right (the
  Engineer popup's own cream is within 20 of it further left). Same window/retry rule as loot.

## Known gaps
- Oracle "Claim" state and reward popup not yet seen live.
- Arena loss popup not yet seen live (the OK poll accepts any wide green button).
- Campaign loot's and Engineer's green Claim not yet seen live (timers were running on 2026-11-11).

# context-mode — MANDATORY routing rules

You have context-mode MCP tools available. These rules are NOT optional — they protect your context window from flooding. A single unrouted command can dump 56 KB into context and waste the entire session.

## BLOCKED commands — do NOT attempt these

### curl / wget — BLOCKED
Any Bash command containing `curl` or `wget` is intercepted and replaced with an error message. Do NOT retry.
Instead use:
- `ctx_fetch_and_index(url, source)` to fetch and index web pages
- `ctx_execute(language: "javascript", code: "const r = await fetch(...)")` to run HTTP calls in sandbox

### Inline HTTP — BLOCKED
Any Bash command containing `fetch('http`, `requests.get(`, `requests.post(`, `http.get(`, or `http.request(` is intercepted and replaced with an error message. Do NOT retry with Bash.
Instead use:
- `ctx_execute(language, code)` to run HTTP calls in sandbox — only stdout enters context

### WebFetch — BLOCKED
WebFetch calls are denied entirely. The URL is extracted and you are told to use `ctx_fetch_and_index` instead.
Instead use:
- `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` to query the indexed content

## REDIRECTED tools — use sandbox equivalents

### Bash (>20 lines output)
Bash is ONLY for: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`, and other short-output commands.
For everything else, use:
- `ctx_batch_execute(commands, queries)` — run multiple commands + search in ONE call
- `ctx_execute(language: "shell", code: "...")` — run in sandbox, only stdout enters context

### Read (for analysis)
If you are reading a file to **Edit** it → Read is correct (Edit needs content in context).
If you are reading to **analyze, explore, or summarize** → use `ctx_execute_file(path, language, code)` instead. Only your printed summary enters context. The raw file content stays in the sandbox.

### Grep (large results)
Grep results can flood context. Use `ctx_execute(language: "shell", code: "grep ...")` to run searches in sandbox. Only your printed summary enters context.

## Tool selection hierarchy

1. **GATHER**: `ctx_batch_execute(commands, queries)` — Primary tool. Runs all commands, auto-indexes output, returns search results. ONE call replaces 30+ individual calls.
2. **FOLLOW-UP**: `ctx_search(queries: ["q1", "q2", ...])` — Query indexed content. Pass ALL questions as array in ONE call.
3. **PROCESSING**: `ctx_execute(language, code)` | `ctx_execute_file(path, language, code)` — Sandbox execution. Only stdout enters context.
4. **WEB**: `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` — Fetch, chunk, index, query. Raw HTML never enters context.
5. **INDEX**: `ctx_index(content, source)` — Store content in FTS5 knowledge base for later search.

## Subagent routing

When spawning subagents (Agent/Task tool), the routing block is automatically injected into their prompt. Bash-type subagents are upgraded to general-purpose so they have access to MCP tools. You do NOT need to manually instruct subagents about context-mode.

## Output constraints

- Keep responses under 500 words.
- Write artifacts (code, configs, PRDs) to FILES — never return them as inline text. Return only: file path + 1-line description.
- When indexing content, use descriptive source labels so others can `ctx_search(source: "label")` later.

## ctx commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call the `ctx_stats` MCP tool and display the full output verbatim |
| `ctx doctor` | Call the `ctx_doctor` MCP tool, run the returned shell command, display as checklist |
| `ctx upgrade` | Call the `ctx_upgrade` MCP tool, run the returned shell command, display as checklist |
