from conftest import blank, paint

from firestone_clicker import atlas, vision


def test_match_mask_exact_and_tolerance():
    img = blank()
    paint(img, (10, 10, 20, 20), 0x0AA008)
    assert vision.any_match(img[10:21, 10:21], 0x0AA008, 0)
    assert vision.any_match(img[10:21, 10:21], 0x0DA30B, 3)
    assert not vision.any_match(img[10:21, 10:21], 0x0DA30B, 2)


def test_probe_inverted_corners():
    p = atlas.Probe(450, 410, 380, 490, atlas.RED_DOT, 32)
    assert p.rect == (380, 410, 450, 490)


def test_green_boxes_two_side_by_side():
    img = blank()
    paint(img, (100, 100, 300, 160), 0x0AA008)
    paint(img, (400, 100, 600, 160), 0x0AA008)
    boxes = vision.green_boxes(img[0:200, 0:700], origin=(0, 0))
    assert len(boxes) == 2 and boxes[0][0] == 100 and boxes[1][0] == 400


def test_blobs_separate_stacked_icons():
    img = blank()
    paint(img, (100, 100, 150, 150), 0xF07070)
    paint(img, (110, 300, 160, 350), 0xF07070)  # same columns, lower down
    paint(img, (500, 100, 505, 105), 0xF07070)  # too small
    found = sorted(vision.blobs(img, (0, 0), 0xF07070, 24, 30))
    assert len(found) == 2
    assert 95 <= found[0][0] <= 100 and 95 <= found[0][1] <= 100
    assert 295 <= found[1][1] <= 300


def test_gem_share_purple_vs_green():
    g = blank()[0:10, 0:10].copy()
    paint(g, (0, 0, 9, 9), 0x0AA008)
    p = blank()[0:10, 0:10].copy()
    paint(p, (0, 0, 9, 9), 0xC040E0)
    assert vision.gem_share(g) == 0.0 and vision.gem_share(p) == 1.0
