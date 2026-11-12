# Changelog

The section for a version becomes the GitHub release notes. Write it for players, not for
developers: what the bot now does differently, what was fixed, what to change in settings.

## 0.1.4 - 2026-11-12

**New**
- Market: opens the Market on the main screen, claims the free Mystery box on the
  first tab and presses the daily Check In on the calendar tab.
- Oracle's gift: opens the Oracle's Market tab in town and claims its free box.
- Both run twice a day by default (`[market]` and `[oracle_gift]` `run_at = [1, 13]`)
  and are remembered in `state.json` like the other daily features. Add the two
  sections to your settings.toml only if you want different hours; the defaults
  apply when they are missing.

## 0.1.3 - 2026-11-11

**New**
- Arena of Kings: fights the opponent at the position you choose (`[arena] opponent`,
  1 strongest to 3 weakest) until the day's attempts are used. Never buys attempts.
- Free pickaxes: claims them from the guild market's Supplies tab.
- Daily missions: clears both Dungeon fights and every Liberation card.
- Campaign loot: claims the "Next loot" chest when its timer is up.
- Engineer: claims the tools production when its timer is up.
- Scheduling: these run only at the hours listed in their `run_at` setting (arena,
  pickaxes and daily missions twice a day, loot and engineer four times) and remember
  what they already did in `state.json`, so a restart does not repeat them.

**Changed**
- Research: skips the tree when both slots are already busy and stops panning
  right as soon as a locked box is in view.

## 0.1.2 - 2026-11-06

**Fixed**
- Map: missions at the far right of the map (the Celenis island) were never opened; the
  scan now reaches them.
- Map: the "Your squads are idling" banner could look like a row of mission pins when it
  sat high on the screen. The scan now stops at the banner's top edge.
- Map: Scout and other small pins were found only now and then (2 frames in 8). Pins are
  now judged by their real pixels, so every mission on screen is found every time.
- Research: a start that hits the "slots full" dialog is no longer logged as started.

**Changed**
- Research: starts are spread across the tree instead of always going to the top box.
  The bot drags the tree to its right end, picks the rightmost column that has available
  research, and within it the one with the lowest level. Columns unlock on levels in the
  column before, so this pushes the tree forward evenly.

## 0.1.1 - 2026-11-05

Map missions only. Everything else is unchanged.

**Fixed**
- Adventure, Naval and some other missions were never opened: their icon colours matched
  the terrain or sea. Every mission icon is now found by the pin under it, whatever the
  picture on it.
- The Naval mission at the bottom of the map was missed exactly when squads were idle,
  because the "Your squads are idling" banner covered its pin. It is now detected anyway.
- Clicks sometimes opened the neighbouring in-progress mission instead of the intended one.
  The click point moved lower on the icon; 10 of 10 test clicks hit the right mission.

**Changed**
- Monster, Naval and Dragon missions are opened first, then Scout, Adventure and War
  missions top to bottom, so idle squads go to the long, valuable missions before the
  short ones. Titan missions are not handled yet (locked until 5B gear power).

## 0.1.0 - 2026-11-04

First release.

**What it automates, every cycle**
- Heroes: presses every green Upgrade button in the heroes menu.
- Guild: claims and restarts expeditions, awakens heroes when affordable, buys personal tree
  nodes (off by default).
- Guardian: evolves when the red dot shows and trains the guardian you pick.
- Alchemist: collects finished experiments and starts new ones, skipping unaffordable ones.
- Oracle: claims finished rituals and starts free ones.
- Research: claims finished research and starts what is available.
- Map missions: claims finished missions and sends idle squads on new ones.

**Safety**
- Never spends gems: every button that could cost gems is checked before it is clicked.
- Never drags the map, never reads game memory, never talks to the network.
- Stops with Win+Esc or Ctrl+C. Gives up and exits if the game window is lost.

**How to use**
- Unzip, edit `settings.toml` to turn features on or off, start the game, run the exe.
- `FirestoneClicker.exe --check` confirms the game window and navigation before a full run.
- Requires Windows, the Epic or Steam game, a 1920x1080 monitor at 100% scaling, the game
  windowed, and the classic hero menu layout.
