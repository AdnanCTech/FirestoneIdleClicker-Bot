"""Find and focus the Firestone window (Windows only, ctypes user32 + psutil)."""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import sys

import psutil

PROCESS_NAMES = ("Firestone.exe",)
Rect = tuple[int, int, int, int]  # screen x, y, w, h


class BadWindow(Exception):
    pass


if sys.platform == "win32":
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    # Per-monitor v2 DPI awareness so client rects and mss captures are in physical pixels.
    user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    _ENUM_PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
else:  # pragma: no cover
    user32 = kernel32 = None


def check_client(rect: Rect) -> None:
    _, _, w, h = rect
    if w != 1920 or not 1000 <= h <= 1040:
        raise BadWindow(f"client is {w}x{h}; need 1920x1009 (windowed, maximized, 1080p, 100% DPI)")


def _game_pids() -> set[int]:
    return {p.pid for p in psutil.process_iter(["name"]) if p.info["name"] in PROCESS_NAMES}


def client_rect(hwnd: int) -> Rect:
    r = wt.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(r))
    pt = wt.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return (pt.x, pt.y, r.right - r.left, r.bottom - r.top)


def find_game_window() -> int | None:
    """HWND of the largest visible, unowned top-level window of Firestone.exe."""
    pids = _game_pids()
    if not pids:
        return None
    best: tuple[int, int] | None = None

    def cb(hwnd, _):
        nonlocal best
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in pids and user32.IsWindowVisible(hwnd) and not user32.GetWindow(hwnd, 4):
            _, _, w, h = client_rect(hwnd)
            if best is None or w * h > best[1]:
                best = (hwnd, w * h)
        return True

    user32.EnumWindows(_ENUM_PROC(cb), 0)
    return best[0] if best else None


def activate(hwnd: int) -> None:
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    if user32.SetForegroundWindow(hwnd):
        return
    # Refused: attach to the foreground thread's input queue and retry.
    fg = user32.GetForegroundWindow()
    fg_thread = user32.GetWindowThreadProcessId(fg, None)
    me = kernel32.GetCurrentThreadId()
    user32.AttachThreadInput(me, fg_thread, True)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    user32.AttachThreadInput(me, fg_thread, False)


def maximize(hwnd: int, timeout_s: float = 5.0) -> Rect:
    """Maximize and wait for the client to reach the reference size; Unity resizes lazily."""
    import time

    user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
    end = time.monotonic() + timeout_s
    while True:
        rect = client_rect(hwnd)
        try:
            check_client(rect)
            time.sleep(1.5)  # let the swap chain settle before the first capture
            return rect
        except BadWindow:
            if time.monotonic() > end:
                raise
            time.sleep(0.25)


def is_foreground(hwnd: int) -> bool:
    return user32.GetForegroundWindow() == hwnd
