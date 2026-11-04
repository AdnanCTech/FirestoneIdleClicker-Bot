# Changelog

The section for a version becomes the GitHub release notes. Write it for players, not for
developers: what the bot now does differently, what was fixed, what to change in settings.

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
