"""The side effects (grab, click/move/drag, key, sleep) behind one object so features are testable."""

from __future__ import annotations

import logging
import threading
import time

import numpy as np

from firestone_clicker import atlas, win

Rect = tuple[int, int, int, int]
log = logging.getLogger("firestone")


class Stopped(Exception):
    pass


class Ctx:
    dry_run: bool = False

    def __init__(self) -> None:
        self.stop = threading.Event()

    def grab(self, rect: Rect) -> np.ndarray:  # inclusive logical rect -> BGRA
        raise NotImplementedError

    def move(self, x: int, y: int) -> None:
        raise NotImplementedError

    def click(self, x: int, y: int) -> None:
        raise NotImplementedError

    def drag(self, x1: int, y1: int, x2: int, y2: int) -> None:
        raise NotImplementedError

    def key(self, name: str) -> None:
        raise NotImplementedError

    def key_hold(self, name: str, ms: int) -> None:
        raise NotImplementedError

    def sleep(self, ms: float) -> None:
        raise NotImplementedError

    def log(self, msg: str) -> None:
        log.info(msg)


class LiveCtx(Ctx):
    def __init__(self, dry_run: bool = False) -> None:
        super().__init__()
        self.dry_run = dry_run
        self.offset = (0, 0)
        self._sct = None
        self._mouse = None
        self._kb = None

    def attach(self, client: win.Rect) -> None:
        self.offset = (client[0] - atlas.REF_ORIGIN[0], client[1] - atlas.REF_ORIGIN[1])

    @classmethod
    def connect(cls, dry_run: bool = False) -> "LiveCtx":
        """Find, focus and maximize the game, then return a context bound to its client area."""
        hwnd = win.find_game_window()
        if hwnd is None:
            raise win.BadWindow("Firestone.exe window not found")
        win.activate(hwnd)
        ctx = cls(dry_run=dry_run)
        ctx.hwnd = hwnd
        ctx.attach(win.maximize(hwnd))
        return ctx

    def save_png(self, path: str) -> None:
        import mss.tools

        img = self.grab((0, atlas.REF_ORIGIN[1], 1919, atlas.REF_ORIGIN[1] + atlas.REF_SIZE[1] - 1))
        mss.tools.to_png(img[:, :, [2, 1, 0]].tobytes(), (img.shape[1], img.shape[0]), output=path)

    def _screen(self, x: int, y: int) -> tuple[int, int]:
        return x + self.offset[0], y + self.offset[1]

    def grab(self, rect: Rect) -> np.ndarray:
        import mss

        if self._sct is None:
            self._sct = mss.mss()
        x1, y1, x2, y2 = rect
        sx, sy = self._screen(x1, y1)
        shot = self._sct.grab({"left": sx, "top": sy, "width": x2 - x1 + 1, "height": y2 - y1 + 1})
        return np.frombuffer(shot.raw, dtype=np.uint8).reshape(shot.height, shot.width, 4)

    def _devices(self):
        if self._mouse is None:
            from pynput import keyboard, mouse

            self._mouse = mouse.Controller()
            self._kb = keyboard.Controller()
            self._Button = mouse.Button
            self._Key = keyboard.Key
        return self._mouse, self._kb

    def _keyobj(self, name: str):
        return getattr(self._Key, name) if len(name) > 1 else name

    def move(self, x: int, y: int) -> None:
        if self.dry_run:
            self.log(f"dry: move {x},{y}")
            return
        m, _ = self._devices()
        m.position = self._screen(x, y)

    def click(self, x: int, y: int) -> None:
        if self.dry_run:
            self.log(f"dry: click {x},{y}")
            return
        m, _ = self._devices()
        m.position = self._screen(x, y)
        m.click(self._Button.left)

    def drag(self, x1: int, y1: int, x2: int, y2: int) -> None:
        if self.dry_run:
            self.log(f"dry: drag {x1},{y1} -> {x2},{y2}")
            return
        m, _ = self._devices()
        m.position = self._screen(x1, y1)
        time.sleep(0.15)
        m.press(self._Button.left)
        time.sleep(0.15)
        steps = 20  # Unity needs the pointer to travel, not jump, to treat it as a pan
        for i in range(1, steps + 1):
            m.position = self._screen(x1 + (x2 - x1) * i // steps, y1 + (y2 - y1) * i // steps)
            time.sleep(0.02)
        time.sleep(0.15)
        m.release(self._Button.left)

    def key(self, name: str) -> None:
        if self.dry_run:
            self.log(f"dry: key {name}")
            return
        _, kb = self._devices()
        kb.tap(self._keyobj(name))

    def key_hold(self, name: str, ms: int) -> None:
        if self.dry_run:
            self.log(f"dry: hold {name} {ms}ms")
            return
        _, kb = self._devices()
        k = self._keyobj(name)
        kb.press(k)
        try:
            self.sleep(ms)
        finally:
            kb.release(k)

    def sleep(self, ms: float) -> None:
        end = time.monotonic() + ms / 1000
        while True:
            if self.stop.is_set():
                raise Stopped()
            left = end - time.monotonic()
            if left <= 0:
                return
            self.stop.wait(min(0.1, left))


class FakeCtx(Ctx):
    """Scripted screens: each click advances to the next screen while one remains."""

    def __init__(self, screens: list[np.ndarray]) -> None:
        super().__init__()
        self.screens = screens
        self.i = 0
        self.clicks: list[tuple[int, int]] = []
        self.drags: list[tuple[int, int, int, int]] = []
        self.moves: list[tuple[int, int]] = []
        self.keys: list[str] = []
        self.key_holds: list[tuple[str, int]] = []
        self.sleeps: list[float] = []
        self.logs: list[str] = []
        self.saved: list[str] = []

    def grab(self, rect: Rect) -> np.ndarray:
        x1, y1, x2, y2 = rect
        return self.screens[self.i][y1 : y2 + 1, x1 : x2 + 1]

    def move(self, x: int, y: int) -> None:
        self.moves.append((x, y))

    def click(self, x: int, y: int) -> None:
        self.clicks.append((x, y))
        if self.i + 1 < len(self.screens):
            self.i += 1

    def drag(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.drags.append((x1, y1, x2, y2))
        if self.i + 1 < len(self.screens):
            self.i += 1

    def key(self, name: str) -> None:
        self.keys.append(name)

    def key_hold(self, name: str, ms: int) -> None:
        self.key_holds.append((name, ms))

    def sleep(self, ms: float) -> None:
        self.sleeps.append(ms)

    def log(self, msg: str) -> None:
        self.logs.append(msg)

    def save_png(self, path: str) -> None:
        self.saved.append(path)


def install_hotkey(stop: threading.Event) -> None:
    """Win+Esc sets the stop event."""
    from pynput import keyboard

    held: set = set()

    def on_press(k):
        held.add(k)
        if k == keyboard.Key.esc and (keyboard.Key.cmd in held or keyboard.Key.cmd_l in held or keyboard.Key.cmd_r in held):
            stop.set()

    def on_release(k):
        held.discard(k)

    keyboard.Listener(on_press=on_press, on_release=on_release, daemon=True).start()
