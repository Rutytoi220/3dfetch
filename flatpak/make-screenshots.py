#!/usr/bin/env python3
"""Render the app's output into a PNG for the Flathub listing.

Runs the app, turns its ANSI output into a grid of coloured cells, writes
that out as SVG and converts it with rsvg-convert.

    ./flatpak/make-screenshots.py arch ubuntu bazzite
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "flatpak" / "screenshots"

# Terminal palette for the basic 16 colours.
PALETTE = {
    30: "#1c1c1c", 31: "#cc3333", 32: "#33aa33", 33: "#ccaa33",
    34: "#3366cc", 35: "#aa33cc", 36: "#22aaaa", 37: "#dddddd",
    90: "#666666", 91: "#ff5555", 92: "#55dd55", 93: "#ffff55",
    94: "#5599ff", 95: "#dd55ff", 96: "#55eeee", 97: "#ffffff",
}
DEFAULT_FG = "#dddddd"
BACKGROUND = "#12141a"
CHROME = "#1c1f27"

CELL_W = 8.4
CELL_H = 17.0
PADDING = 18
TITLE_H = 26


def parse(text):
    """Turn ANSI output into a list of rows of (character, colour)."""
    rows = []
    row = []
    colour = DEFAULT_FG
    sgr = re.compile(r"\x1b\[([0-9;?]*)([a-zA-Z])")
    index = 0
    while index < len(text):
        match = sgr.match(text, index)
        if match:
            params, command = match.group(1), match.group(2)
            if command == "m" and not params.startswith("?"):
                colour = apply_sgr(colour, params)
            index = match.end()
            continue
        char = text[index]
        index += 1
        if char == "\n":
            rows.append(row)
            row = []
        elif char == "\r":
            continue
        elif char == "\x1b":
            continue
        else:
            row.append((char, colour))
    if row:
        rows.append(row)
    return rows


def apply_sgr(colour, params):
    if params == "":
        params = "0"
    codes = [int(p) for p in params.split(";") if p != ""]
    index = 0
    while index < len(codes):
        code = codes[index]
        if code == 0:
            colour = DEFAULT_FG
        elif code in PALETTE:
            colour = PALETTE[code]
        elif code == 38 and index + 4 < len(codes) and codes[index + 1] == 2:
            r, g, b = codes[index + 2], codes[index + 3], codes[index + 4]
            colour = "#%02x%02x%02x" % (r, g, b)
            index += 4
        index += 1
    return colour


def escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def to_svg(rows, title):
    width = max((len(r) for r in rows), default=80)
    height = len(rows) * CELL_H
    total_w = width * CELL_W + PADDING * 2
    total_h = height + PADDING * 2 + TITLE_H

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" '
        f'height="{total_h:.0f}" viewBox="0 0 {total_w:.0f} {total_h:.0f}">',
        f'<rect width="{total_w:.0f}" height="{total_h:.0f}" rx="10" fill="{CHROME}"/>',
        f'<rect x="0" y="0" width="{total_w:.0f}" height="{TITLE_H}" rx="10" '
        f'fill="#262a34"/>',
        f'<rect x="0" y="{TITLE_H - 10}" width="{total_w:.0f}" height="10" fill="#262a34"/>',
    ]
    # Window buttons.
    for index, dot in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        out.append(f'<circle cx="{18 + index * 16}" cy="{TITLE_H / 2}" r="5" fill="{dot}"/>')
    out.append(
        f'<text x="{total_w / 2:.0f}" y="{TITLE_H / 2 + 4:.0f}" fill="#9aa0aa" '
        f'font-family="DejaVu Sans Mono, monospace" font-size="11" '
        f'text-anchor="middle">{escape(title)}</text>'
    )

    out.append(
        f'<g font-family="DejaVu Sans Mono, monospace" font-size="14" '
        f'xml:space="preserve">'
    )
    for r, row in enumerate(rows):
        y = PADDING + TITLE_H + r * CELL_H + CELL_H - 4
        for c, (char, colour) in enumerate(row):
            if char == " ":
                continue
            x = PADDING + c * CELL_W
            out.append(
                f'<text x="{x:.1f}" y="{y:.1f}" fill="{colour}">{escape(char)}</text>'
            )
    out.append("</g>")
    out.append("</svg>")
    return "\n".join(out)


def main():
    logos = sys.argv[1:] or ["arch", "ubuntu", "bazzite"]
    OUT.mkdir(parents=True, exist_ok=True)
    for logo in logos:
        result = subprocess.run(
            [str(ROOT / "fetch"), "--frames", "1", "--logo", logo],
            capture_output=True, text=True, timeout=60,
        )
        rows = parse(result.stdout)
        svg = to_svg(rows, f"3dfetch")
        with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as handle:
            handle.write(svg)
            svg_path = handle.name
        png = OUT / f"{logo}.png"
        subprocess.run(
            ["rsvg-convert", "-w", "1400", "-o", str(png), svg_path], check=True
        )
        Path(svg_path).unlink()
        print(f"wrote {png}")


if __name__ == "__main__":
    main()
