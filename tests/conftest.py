import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def blank() -> np.ndarray:
    img = np.zeros((1080, 1920, 4), dtype=np.uint8)
    img[:, :, 3] = 255
    return img


def paint(img: np.ndarray, rect: tuple[int, int, int, int], color: int) -> None:
    x1, y1, x2, y2 = rect
    r, g, b = (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
    img[y1 : y2 + 1, x1 : x2 + 1, 0] = b
    img[y1 : y2 + 1, x1 : x2 + 1, 1] = g
    img[y1 : y2 + 1, x1 : x2 + 1, 2] = r
