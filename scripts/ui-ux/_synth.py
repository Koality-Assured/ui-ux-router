"""Shared synthetic UI fixture helpers for visual and a11y gates.

Not indexed (underscore prefix). Deterministic PNG raster + WCAG contrast.
Playwright/axe-core remain optional engines; this path stays OS-stable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import zlib
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

VIEWPORTS = (375, 768, 1280, 1920)
CANVAS_HEIGHT = 80
PIXEL_THRESHOLD = 0.1
AA_CONTRAST = 4.5
MIN_TARGET_PX = 24

HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def fixture_root(root: Path | None = None) -> Path:
    base = root or repo_root()
    return base / "scripts" / "ui-ux" / "fixtures"


def component_dir(root: Path | None = None) -> Path:
    return fixture_root(root) / "components"


def baseline_dir(root: Path | None = None) -> Path:
    return fixture_root(root) / "baselines"


def token_path(root: Path | None = None) -> Path:
    return fixture_root(root) / "tokens" / "tokens.json"


def parse_hex(color: str) -> tuple[int, int, int]:
    raw = color.strip()
    if raw.lower() in {"white", "#fff", "#ffffff"}:
        return (255, 255, 255)
    if raw.lower() in {"black", "#000", "#000000"}:
        return (0, 0, 0)
    match = HEX_RE.match(raw)
    if not match:
        raise ValueError(f"unsupported color {color!r}")
    h = match.group(1)
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    def channel(value: int) -> float:
        s = value / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    lighter, darker = (l1, l2) if l1 >= l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)


@dataclass
class Box:
    role: str
    text: str
    x: int
    y: int
    w: int
    h: int
    bg: tuple[int, int, int]
    fg: tuple[int, int, int]
    attrs: dict[str, str]


class FixtureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.page_bg = (244, 244, 244)
        self.lang = "en"
        self.has_main = False
        self.has_dialog = False
        self.keyboard_trap = False
        self.boxes: list[Box] = []
        self.unlabeled_controls = 0
        self.labeled_controls = 0
        self._capture: str | None = None
        self._buf: list[str] = []
        self._current: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k: (v or "") for k, v in attrs}
        if tag == "html" and ad.get("lang"):
            self.lang = ad["lang"]
        if tag == "body" and ad.get("data-bg"):
            self.page_bg = parse_hex(ad["data-bg"])
        if tag == "main":
            self.has_main = True
        if tag == "dialog" or ad.get("role") == "dialog":
            self.has_dialog = True
        if ad.get("data-keyboard-trap", "").lower() in {"1", "true", "yes"}:
            self.keyboard_trap = True
        onkeydown = ad.get("onkeydown", "")
        if "preventDefault" in onkeydown and "Tab" in onkeydown:
            self.keyboard_trap = True
        role = ad.get("data-role") or ad.get("role") or tag
        if role in {"button", "textbox", "input", "modal", "dialog", "label"} or tag in {
            "button",
            "input",
            "textarea",
        }:
            self._current = {"tag": tag, "role": role, **ad}
            self._capture = role
            self._buf = []
            if tag in {"input", "textarea", "select"}:
                if ad.get("aria-label") or ad.get("id"):
                    self.labeled_controls += 1
                else:
                    self.unlabeled_controls += 1
        if tag == "label":
            self.labeled_controls += 1

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._current is None:
            return
        if tag != self._current.get("tag") and tag not in {"button", "label"}:
            return
        ad = self._current
        text = "".join(self._buf).strip()
        w = int(ad.get("data-w") or "48")
        h = int(ad.get("data-h") or "48")
        bg = parse_hex(ad.get("data-bg") or "#0b57d0")
        fg = parse_hex(ad.get("data-fg") or "#ffffff")
        self.boxes.append(
            Box(
                role=ad.get("role") or ad.get("data-role") or tag,
                text=text,
                x=0,
                y=0,
                w=w,
                h=h,
                bg=bg,
                fg=fg,
                attrs=ad,
            )
        )
        self._current = None
        self._capture = None
        self._buf = []


def parse_fixture(html: str) -> FixtureParser:
    parser = FixtureParser()
    parser.feed(html)
    parser.close()
    return parser


def layout_boxes(boxes: list[Box], viewport: int) -> list[Box]:
    laid: list[Box] = []
    x = 8
    y = 8
    row_h = 0
    gap = 8
    for src in boxes:
        box = Box(**{**src.__dict__})
        if viewport <= 375:
            box.x = 8
            box.y = y
            y += box.h + gap
        else:
            if x + box.w + 8 > viewport:
                x = 8
                y += row_h + gap
                row_h = 0
            box.x = x
            box.y = y
            x += box.w + gap
            row_h = max(row_h, box.h)
        laid.append(box)
    return laid


def _put(px: bytearray, width: int, x: int, y: int, rgb: tuple[int, int, int]) -> None:
    if x < 0 or y < 0 or x >= width or y >= CANVAS_HEIGHT:
        return
    i = (y * width + x) * 3
    px[i : i + 3] = bytes(rgb)


def rasterize(html: str, viewport: int) -> bytes:
    parsed = parse_fixture(html)
    digest = hashlib.sha256(html.encode("utf-8")).digest()
    px = bytearray(viewport * CANVAS_HEIGHT * 3)
    for i in range(0, len(px), 3):
        px[i : i + 3] = bytes(parsed.page_bg)
    # Identity strip so HTML edits change pixels even when boxes match.
    for x in range(viewport):
        tone = digest[x % len(digest)]
        _put(px, viewport, x, 0, (tone, parsed.page_bg[1], parsed.page_bg[2]))
    for box in layout_boxes(parsed.boxes, viewport):
        for yy in range(box.h):
            for xx in range(box.w):
                _put(px, viewport, box.x + xx, box.y + yy + 2, box.bg)
        for xx in range(min(box.w, max(4, len(box.text) * 4))):
            _put(px, viewport, box.x + 4 + xx, box.y + max(4, box.h // 2) + 2, box.fg)
    return bytes(px)


def encode_png(width: int, height: int, rgb: bytes) -> bytes:
    if len(rgb) != width * height * 3:
        raise ValueError("rgb buffer size mismatch")
    raw = b"".join(
        b"\x00" + rgb[y * width * 3 : (y + 1) * width * 3] for y in range(height)
    )

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def decode_png_rgb(data: bytes) -> tuple[int, int, bytes]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG")
    offset = 8
    width = height = None
    raw = bytearray()
    while offset < len(data):
        (length,) = struct.unpack(">I", data[offset : offset + 4])
        tag = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if tag == b"IHDR":
            width, height, bit_depth, color_type, *_ = struct.unpack(">IIBBBBB", payload)
            if bit_depth != 8 or color_type != 2:
                raise ValueError("only 8-bit RGB PNG supported")
        elif tag == b"IDAT":
            raw.extend(payload)
        elif tag == b"IEND":
            break
    if width is None or height is None:
        raise ValueError("missing IHDR")
    decompressed = zlib.decompress(bytes(raw))
    rgb = bytearray()
    stride = width * 3
    pos = 0
    for _ in range(height):
        pos += 1  # filter byte (expect 0)
        rgb.extend(decompressed[pos : pos + stride])
        pos += stride
    return width, height, bytes(rgb)


def diff_pixels(left: bytes, right: bytes, *, threshold: float = PIXEL_THRESHOLD) -> int:
    if len(left) != len(right):
        return max(len(left), len(right)) // 3
    cutoff = int(threshold * 255)
    mismatches = 0
    for i in range(0, len(left), 3):
        delta = max(abs(left[j] - right[j]) for j in range(i, i + 3))
        if delta > cutoff:
            mismatches += 1
    return mismatches


def list_component_html(root: Path | None = None) -> list[Path]:
    return sorted(component_dir(root).glob("*.html"))


def baseline_name(html_path: Path, viewport: int) -> str:
    return f"{html_path.stem}-{viewport}w.png"


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def add_json_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--dry-run", action="store_true", help="Report without writing files")
