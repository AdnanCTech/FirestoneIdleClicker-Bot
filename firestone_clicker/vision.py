"""Pixel matching on BGRA numpy images (what mss returns)."""

from __future__ import annotations

import numpy as np

from firestone_clicker import atlas

Rect = tuple[int, int, int, int]


def color_rgb(color: int) -> tuple[int, int, int]:
    return (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF


def match_mask(img: np.ndarray, color: int, var: int) -> np.ndarray:
    r, g, b = color_rgb(color)
    px = img[:, :, :3].astype(np.int16)
    return (
        (np.abs(px[:, :, 2] - r) <= var)
        & (np.abs(px[:, :, 1] - g) <= var)
        & (np.abs(px[:, :, 0] - b) <= var)
    )


def any_match(img: np.ndarray, color: int, var: int) -> bool:
    return bool(match_mask(img, color, var).any())


def color_share(img: np.ndarray, color: int, var: int) -> float:
    m = match_mask(img, color, var)
    return float(m.mean()) if m.size else 0.0


def gem_share(img: np.ndarray) -> float:
    """Share of purple pixels (gem icon): R and B high, G well below both."""
    px = img[:, :, :3].astype(np.int16)
    b, g, r = px[:, :, 0], px[:, :, 1], px[:, :, 2]
    m = (r > 120) & (b > 120) & (g < r - 60) & (g < b - 60)
    return float(m.mean()) if m.size else 0.0


def grey_share(img: np.ndarray) -> float:
    """Share of mid-grey pixels (a disabled / unaffordable button)."""
    px = img[:, :, :3].astype(np.int16)
    spread = px.max(axis=2) - px.min(axis=2)
    mean = px.mean(axis=2)
    m = (spread < 18) & (mean > 60) & (mean < 200)
    return float(m.mean()) if m.size else 0.0


def color_boxes(
    img: np.ndarray,
    origin: tuple[int, int],
    color: int,
    var: int,
    min_w: int,
    min_h: int,
    fill: float = 0.5,
) -> list[Rect]:
    """Logical rects of solid same-coloured boxes inside `img`, left to right.

    Column projection of the colour mask, so boxes side by side are told apart; two boxes
    stacked in the same columns would merge into one.
    """
    mask = match_mask(img, color, var)
    h, w = mask.shape
    if not h or not w:
        return []
    ox, oy = origin
    cols = mask.sum(axis=0) >= min_h * fill
    out: list[Rect] = []
    start = None
    for i, on in enumerate(list(cols) + [False]):
        if on and start is None:
            start = i
        elif not on and start is not None:
            if i - start >= min_w:
                band = mask[:, start:i]
                rows = np.nonzero(band.sum(axis=1) >= (i - start) * fill)[0]
                if len(rows) >= min_h:
                    out.append((ox + start, oy + int(rows[0]), ox + i - 1, oy + int(rows[-1])))
            start = None
    return out


def blobs(
    img: np.ndarray,
    origin: tuple[int, int],
    color: int,
    var: int,
    min_px: int,
    cell: int = 8,
    cell_fill: float = 0.3,
) -> list[Rect]:
    """Logical bounding rects of connected colour blobs (cell grid + flood fill).

    Unlike color_boxes this separates blobs that share columns, e.g. icons stacked on a map.
    """
    mask = match_mask(img, color, var)
    h, w = mask.shape
    gh, gw = h // cell, w // cell
    if not gh or not gw:
        return []
    cells = mask[: gh * cell, : gw * cell].reshape(gh, cell, gw, cell).mean(axis=(1, 3)) >= cell_fill
    seen = np.zeros_like(cells, dtype=bool)
    ox, oy = origin
    out: list[Rect] = []
    for sy, sx in zip(*np.nonzero(cells)):
        if seen[sy, sx]:
            continue
        stack = [(sy, sx)]
        seen[sy, sx] = True
        ys, xs = [], []
        while stack:
            y, x = stack.pop()
            ys.append(y)
            xs.append(x)
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < gh and 0 <= nx < gw and cells[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        x1, x2 = int(min(xs)) * cell, (int(max(xs)) + 1) * cell - 1
        y1, y2 = int(min(ys)) * cell, (int(max(ys)) + 1) * cell - 1
        if x2 - x1 + 1 >= min_px and y2 - y1 + 1 >= min_px:
            out.append((ox + x1, oy + y1, ox + x2, oy + y2))
    return out


def green_boxes(
    img: np.ndarray, origin: tuple[int, int], min_w: int = 100, min_h: int = 25, var: int = 30
) -> list[Rect]:
    return color_boxes(img, origin, atlas.GREEN_BUTTON, var, min_w, min_h)
