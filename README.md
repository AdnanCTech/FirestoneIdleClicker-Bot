# FirestoneClicker

A small bot that keeps Firestone Idle RPG progressing while you are away. It looks at the
screen and clicks, like a player would. It never spends gems, never drags the map, and never
reads game memory or talks to the network.

## What it does, each cycle

- Heroes: presses every green Upgrade button in the heroes menu.
- Guild: claims and restarts expeditions, awakens heroes when affordable, buys personal tree
  nodes (off by default).
- Guardian: evolves when the red dot shows, trains the guardian you pick.
- Alchemist: collects finished experiments, completes free speed-ups, starts new ones.
- Oracle: claims and starts rituals.
- Research: claims finished research and starts any available one in view.
- Map: claims finished missions and starts new ones while squads are idle.

Then it pauses (60 seconds by default) and goes again.

## Requirements

- Windows 10 or 11.
- Firestone from Epic or Steam, already running, in English.
- A 1920x1080 monitor at 100% display scaling. The bot maximizes the game window itself.
- The classic hero menu (the one opened with the U key). The "new adventure" layout with hero
  cards along the bottom is not supported.
- Account level 200 or higher so every feature is unlocked.

The bot refuses to start, with a message saying why, when the game is not running or the
window is not 1920x1080.

## Install and run

1. Download `FirestoneClicker-<version>-win64.zip` from the Releases page and unzip it anywhere.
2. Open `settings.toml` (next to the exe) in any text editor and turn off what you do not want.
   Every feature is on by default except the personal tree.
3. Start Firestone and get to the main screen.
4. Double-click `FirestoneClicker.exe`. A console window shows what it is doing; the same text
   goes to `bot.log` next to the exe.
5. Stop it with Win+Esc or Ctrl+C in the console.

The bot owns the mouse and keyboard while it runs. Do not use the PC for something else at the
same time: keystrokes meant for the game would land in whatever window you clicked.

`settings.toml` controls which features run, which hero slots, alchemist experiments or tree
nodes to use, which guardian to train, and the pause between cycles. Changes apply the next
time you start the bot. If you delete the file, the next run recreates the defaults.

### Windows says it protected your PC

The exe is not code-signed, so SmartScreen shows a warning the first time. Click "More info",
then "Run anyway". Some antivirus tools also flag it because it bundles a keyboard-hook
library used for the Win+Esc stop key. If that worries you, the source is right here: run
`build.ps1` to build the exe yourself.

## Troubleshooting

- `FirestoneClicker.exe --check` reports the window it found, the client size, and whether
  the main-screen markers are visible. Run it on the main screen with no dialog open.
- `FirestoneClicker.exe --once heroes` runs a single feature and exits. Feature names:
  `heroes`, `guild`, `guardian`, `alchemist`, `oracle`, `research`, `map_missions`.
- `FirestoneClicker.exe --dry-run` runs one cycle without clicking anything.
- When a feature fails the bot saves a screenshot in `diag/` and carries on. If it cannot get
  back to the main screen three cycles in a row it stops.

## Running from source

Needs Python 3.12 and [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run pytest -q
uv run python -m firestone_clicker
```

## Credits and licence

MIT, see `LICENSE`. The screen coordinates and colour probes derive from
[Lutakh/firestone-bot](https://github.com/Lutakh/firestone-bot) (MIT), itself a port of
Deaeth85's AutoHotkey Firestone Bot. Automating a game may be against its terms of service;
use at your own risk.
