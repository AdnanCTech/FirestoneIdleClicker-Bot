# FireStoneClicker

Minimal Windows bot for Firestone Idle RPG (Epic build). Pixel probes + simulated input, no
OCR, no GUI, no relaunch. Replaces the bloated Lutakh/firestone-bot with only what the owner
needs. Design: `docs/superpowers/specs/2026-11-04-firestone-clicker-design.md`. Build plan and
ledger of decisions: `docs/superpowers/plans/2026-11-04-firestone-clicker.md`, `diag/sdd-ledger.md`.

## Run / test
- `uv run python -m firestone_clicker` loops until Win+Esc or Ctrl+C. `--once <feature>` runs one
  feature, `--dry-run` runs one cycle with input disabled. Logs to terminal and `bot.log`,
  failure captures to `diag/`. Exit code 1 means it gave up (window lost or stuck).
- `uv run pytest -q` (62 tests, ~3 s). Tests paint fake screens; no game needed.
- `uv run python tools/probe_check.py` prints FOUND/missing for every atlas probe on the live
  screen and draws them on `diag/probe_check.png`. `tools/smoke.py` checks window + capture.
- Game must be running. The bot finds `Firestone.exe`, maximizes it and waits until the client
  is 1920x1009 (Unity resizes lazily). Works on a second monitor at negative coordinates.

## Layout
- `atlas.py` every coordinate/colour, grouped per feature, with "measured live" notes.
- `vision.py` numpy matching on BGRA: `match_mask`, `color_boxes` (column projection; merges
  vertically stacked shapes), `blobs` (connected components; use for map icons), `gem_share`,
  `grey_share`.
- `ctx.py` `Ctx` = the four side effects (grab, click/move, key, sleep). `LiveCtx` (mss +
  pynput + `win.py`), `FakeCtx` for tests (each click advances to the next scripted screen,
  so fixtures are off-by-one prone: count the opening clicks).
- `nav.py` `found`, `wait_for`, `click`, `safe_click` (gem gate), `go_home`, `open_town`,
  `require_screen`, `find_dialog_x`.
- `features/*.py` one `run(ctx, cfg)` each. `loop.py` cycle order and exit rules.
- `settings.toml` is the only config; `config.py` rejects unknown keys in known sections.

## Rules learned the hard way
- Logical coords == screen coords only when the client origin is (0,31); `LiveCtx.offset`
  handles the rest. Never hardcode screen coords.
- Every button that could spend anything goes through `nav.safe_click` (gem check on its rect).
  Never click an orange button; grey means unaffordable (alchemist `grey_share`).
- `go_home` clicks only `BIG_CLOSE (1851,84)`; a whole-screen orange-ring search matched the
  Guild market roof and opened it. Dialog-X search is only safe in narrow feature bands.
- Reference-bot coordinates are not trusted until seen live: the personal tree, map and troop
  marker all differed. Check with `probe_check.py`, then a `--once` run, before relying on one.
- Map: icons are found by colour (`MAP_ICON_COLORS`), gated by the idle banner; the map is
  never dragged. "N/26" at the top is idle squads.
- Personal tree: an out-of-tokens popup puts a green "Get more" under the buy point; it is
  probed (`PTREE_NEED_MORE`) and closed, never blind-clicked.

## Known gaps
- Research starts only boxes visible without scrolling. Oracle "Claim" state and reward popup
  not yet seen live. Some map scroll icons on the right edge go undetected.

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
