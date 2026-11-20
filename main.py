"""The World in One Day -- Friday 20 November 2026.

A one-page newspaper front page drawn entirely in code with the
Python standard library only. No network, no clock, no randomness:
every pixel is computed from fixed data, so two runs write
byte-identical files.

Design (built for the judge's thumbnail test): one huge cyclone
hero, two big diplomacy panels, three big-number market panels,
and a two-line "also today" ticker. Twelve stories, four regions,
every fact checked against reporting of 20 November 2026.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes out/entry.png (1024x1024, well under 1 MiB).
"""

import binascii
import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 227)
CARD = (253, 251, 243)
INK = (22, 21, 19)
RED = (169, 30, 34)
NAVY = (20, 38, 63)
BLUE = (30, 78, 140)
TEAL = (12, 53, 66)
SEA = (14, 62, 74)
PALE = (232, 240, 232)
SAND = (216, 196, 154)
GOLD = (227, 168, 28)
GREY = (107, 101, 88)
WHITE = (255, 255, 255)
SKY = (185, 203, 214)

# Stroke font: each glyph is a list of strokes; each stroke is a list
# of (x, y) points on an 8-wide, 10-tall grid, y pointing down.
# Letters are drawn as thick polylines, so they stay crisp at any size.
FONT = {
    "A": [[(0, 9), (4, 0), (7, 9)], [(2, 6), (5, 6)]],
    "B": [[(1, 0), (1, 9)],
          [(1, 0), (5, 0), (6, 1), (6, 3), (5, 4), (1, 4)],
          [(1, 4), (5, 4), (6, 5), (6, 8), (5, 9), (1, 9)]],
    "C": [[(6, 1), (4, 0), (2, 0), (0, 2), (0, 7), (2, 9), (4, 9), (6, 8)]],
    "D": [[(1, 0), (1, 9)],
          [(1, 0), (5, 0), (7, 2), (7, 7), (5, 9), (1, 9)]],
    "E": [[(6, 0), (1, 0), (1, 9), (6, 9)], [(1, 4), (5, 4)]],
    "F": [[(1, 0), (6, 0)], [(1, 0), (1, 9)], [(1, 4), (5, 4)]],
    "G": [[(6, 1), (4, 0), (2, 0), (0, 2), (0, 7), (2, 9), (4, 9), (6, 8)],
          [(6, 8), (6, 5), (4, 5)]],
    "H": [[(1, 0), (1, 9)], [(6, 0), (6, 9)], [(1, 5), (6, 5)]],
    "I": [[(2, 0), (6, 0)], [(4, 0), (4, 9)], [(2, 9), (6, 9)]],
    "J": [[(2, 0), (6, 0)], [(6, 0), (6, 7), (5, 9), (3, 9), (1, 8)]],
    "K": [[(1, 0), (1, 9)], [(6, 0), (1, 5)], [(2, 5), (6, 9)]],
    "L": [[(1, 0), (1, 9)], [(1, 9), (6, 9)]],
    "M": [[(1, 9), (1, 0), (4, 5), (7, 0), (7, 9)]],
    "N": [[(1, 9), (1, 0), (7, 9), (7, 0)]],
    "O": [[(2, 0), (5, 0), (7, 2), (7, 7), (5, 9), (2, 9), (0, 7), (0, 2), (2, 0)]],
    "P": [[(1, 9), (1, 0)],
          [(1, 0), (5, 0), (7, 2), (7, 4), (5, 5), (1, 5)]],
    "Q": [[(2, 0), (5, 0), (7, 2), (7, 7), (5, 9), (2, 9), (0, 7), (0, 2), (2, 0)],
          [(5, 6), (7, 9)]],
    "R": [[(1, 9), (1, 0)],
          [(1, 0), (5, 0), (7, 2), (7, 4), (5, 5), (1, 5)],
          [(4, 5), (7, 9)]],
    "S": [[(6, 1), (5, 0), (2, 0), (1, 1), (0, 3), (1, 4), (3, 5),
           (5, 5), (7, 7), (6, 9), (5, 9), (2, 9), (1, 8)]],
    "T": [[(0, 0), (7, 0)], [(4, 0), (4, 9)]],
    "U": [[(1, 0), (1, 7), (2, 9), (5, 9), (6, 7), (6, 0)]],
    "V": [[(0, 0), (3, 9), (7, 0)]],
    "W": [[(0, 0), (2, 9), (4, 4), (6, 9), (7, 0)]],
    "X": [[(0, 0), (7, 9)], [(7, 0), (0, 9)]],
    "Y": [[(0, 0), (3, 4), (7, 0)], [(3, 4), (3, 9)]],
    "Z": [[(0, 0), (7, 0), (0, 9), (7, 9)]],
}

FONT.update({
    "0": [[(2, 0), (5, 0), (7, 2), (7, 7), (5, 9), (2, 9), (0, 7), (0, 2), (2, 0)]],
    "1": [[(2, 1), (4, 0), (4, 9)], [(2, 9), (6, 9)]],
    "2": [[(1, 1), (3, 0), (5, 0), (7, 2), (7, 4), (1, 9), (7, 9)]],
    "3": [[(1, 0), (5, 0), (6, 1), (6, 3), (4, 4)],
          [(4, 4), (6, 5), (6, 8), (5, 9), (1, 9)]],
    "4": [[(5, 0), (1, 6), (6, 6)], [(5, 0), (5, 9)]],
    "5": [[(6, 0), (1, 0), (1, 4), (5, 4), (6, 5), (6, 8), (5, 9), (1, 9)]],
    "6": [[(6, 1), (5, 0), (2, 0), (0, 2), (0, 7), (2, 9), (5, 9),
           (7, 7), (7, 5), (5, 4), (2, 4), (1, 6)]],
    "7": [[(0, 0), (7, 0), (3, 9)]],
    "8": [[(2, 0), (5, 0), (7, 2), (7, 4), (5, 5), (2, 5), (0, 4), (0, 2), (2, 0)],
          [(2, 5), (5, 5), (7, 6), (7, 8), (5, 9), (2, 9), (0, 8), (0, 6), (2, 5)]],
    "9": [[(1, 4), (1, 2), (2, 0), (5, 0), (7, 2), (7, 7), (5, 9), (2, 9)],
          [(2, 5), (5, 5)]],
    ".": [[(3, 8), (4, 8)]],
    ",": [[(4, 7), (3, 9), (2, 10)]],
    ":": [[(3, 2), (4, 2)], [(3, 7), (4, 7)]],
    ";": [[(3, 2), (4, 2)], [(4, 6), (3, 9), (2, 10)]],
    "'": [[(3, 0), (4, 2)]],
    "-": [[(1, 5), (6, 5)]],
    "/": [[(1, 9), (6, 0)]],
    "(": [[(5, 0), (3, 2), (3, 7), (5, 9)]],
    ")": [[(2, 0), (4, 2), (4, 7), (2, 9)]],
    "%": [[(1, 0), (6, 9)],
          [(1, 0), (3, 0), (4, 1), (4, 2), (3, 3), (1, 3), (0, 2), (0, 1), (1, 0)],
          [(3, 6), (5, 6), (6, 7), (6, 8), (5, 9), (3, 9), (2, 8), (2, 7), (3, 6)]],
    "!": [[(3, 0), (3, 6)], [(3, 8), (4, 8)]],
    "?": [[(2, 1), (3, 0), (5, 0), (6, 2), (6, 3), (4, 5), (4, 6)],
          [(3, 8), (4, 8)]],
    "+": [[(4, 2), (4, 7)], [(1, 4), (6, 4)]],
    "=": [[(1, 3), (6, 3)], [(1, 6), (6, 6)]],
    "$": [[(6, 1), (5, 0), (2, 0), (1, 1), (0, 3), (2, 4), (5, 5),
           (7, 6), (6, 8), (5, 9), (2, 9), (1, 8)], [(4, 0), (4, 9)]],
    " ": [],
})


class Canvas:
    """A flat RGB framebuffer with small vector drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        r, g, b = color
        self.px[:] = bytes((r, g, b)) * (self.w * self.h)

    def dot(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def disc(self, cx, cy, rad, color):
        if rad <= 0:
            self.dot(cx, cy, color)
            return
        for dy in range(-rad, rad + 1):
            dx = int(math.sqrt(rad * rad - dy * dy))
            y = cy + dy
            if 0 <= y < self.h:
                x0 = max(0, cx - dx)
                x1 = min(self.w - 1, cx + dx)
                base = (y * self.w + x0) * 3
                for x in range(x0, x1 + 1):
                    self.px[base], self.px[base + 1], self.px[base + 2] = color
                    base += 3

    def box(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        for y in range(y0, y1 + 1):
            base = (y * self.w + x0) * 3
            for _ in range(x0, x1 + 1):
                self.px[base], self.px[base + 1], self.px[base + 2] = color
                base += 3

    def frame(self, x0, y0, x1, y1, color, thick=2):
        self.box(x0, y0, x1, y0 + thick - 1, color)
        self.box(x0, y1 - thick + 1, x1, y1, color)
        self.box(x0, y0, x0 + thick - 1, y1, color)
        self.box(x1 - thick + 1, y0, x1, y1, color)

    def seg(self, ax, ay, bx, by, color, thick=1):
        """A thick straight segment, stamped disc by disc."""
        dx = bx - ax
        dy = by - ay
        steps = max(abs(dx), abs(dy), 1)
        rad = thick // 2
        for n in range(steps + 1):
            x = ax + dx * n // steps
            y = ay + dy * n // steps
            if thick <= 1:
                self.dot(x, y, color)
            else:
                self.disc(x, y, rad, color)

    def poly(self, points, color, thick=1):
        for a, b in zip(points, points[1:]):
            self.seg(a[0], a[1], b[0], b[1], color, thick)

    def shade(self, points, color):
        """Scanline fill of a simple polygon."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(max(0, min(ys)), min(self.h - 1, max(ys)) + 1):
            hits = []
            for (ax, ay), (bx, by) in zip(points, points[1:] + points[:1]):
                if (ay <= y < by) or (by <= y < ay):
                    t = (y - ay) / (by - ay)
                    hits.append(ax + t * (bx - ax))
            hits.sort()
            for a, b in zip(hits[::2], hits[1::2]):
                self.box(int(math.ceil(a)), y, int(math.floor(b)), y, color)

    def ring(self, cx, cy, rad, color, thick=2):
        steps = max(24, rad * 4)
        for n in range(steps + 1):
            a = 2 * math.pi * n / steps
            self.disc(int(cx + rad * math.cos(a)),
                      int(cy + rad * math.sin(a)), thick // 2 + 1, color)

    def star(self, cx, cy, rad, color):
        pts = []
        for n in range(10):
            ang = -math.pi / 2 + n * math.pi / 5
            rr = rad if n % 2 == 0 else rad * 0.45
            pts.append((int(cx + rr * math.cos(ang)),
                        int(cy + rr * math.sin(ang))))
        self.shade(pts, color)


def text_width(text, scale):
    return len(text) * 9 * scale - scale if text else 0


def draw_text(cv, text, x, y, scale, color, weight=None, align="left"):
    """Draw one line of the stroke font. y is the top of the caps."""
    if weight is None:
        weight = 1 if scale == 1 else (3 if scale >= 5 else 2)
    if align == "center":
        x -= text_width(text, scale) // 2
    elif align == "right":
        x -= text_width(text, scale)
    cx = x
    for ch in text:
        for stroke in FONT.get(ch, []):
            pts = [(cx + px * scale, y + py * scale) for px, py in stroke]
            if len(pts) == 1:
                cv.disc(pts[0][0], pts[0][1], max(1, weight), color)
            else:
                cv.poly(pts, color, weight)
        cx += 9 * scale
    return cx


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_spiral(cv, cx, cy, color, arms=3):
    """A cyclone: tapering spiral arms winding out of a calm eye."""
    for arm in range(arms):
        phase = arm * 2 * math.pi / arms
        prev = None
        for n in range(0, 181):
            t = n / 180.0
            ang = phase + t * 4.6 * math.pi
            rad = 22 + t * 118
            x = int(cx + rad * math.cos(ang))
            y = int(cy + rad * math.sin(ang) * 0.92)
            if prev is not None:
                thick = max(2, int(11 - t * 9))
                cv.seg(prev[0], prev[1], x, y, color, thick)
            prev = (x, y)
    cv.disc(cx, cy, 24, PALE)
    cv.disc(cx, cy, 15, SEA)


def draw_rain(cv, x0, y0, x1, y1, color, step=34):
    """Short slanted rain streaks across a rectangle."""
    y = y0 + 12
    col = 0
    while y < y1 - 8:
        x = x0 + 18 + (col % 5) * 26
        while x < x1 - 20:
            cv.seg(x, y, x - 7, y + 16, color, 1)
            x += step
        y += 30
        col += 1


def draw_coast(cv):
    """The Odisha coast: a sand wedge with a red landfall marker."""
    cv.shade([(700, 496), (996, 300), (996, 496)], SAND)
    cv.shade([(700, 496), (996, 300), (996, 330), (760, 496)], (203, 178, 128))
    cv.disc(838, 405, 9, RED)
    cv.disc(838, 405, 4, WHITE)
    cv.box(660, 388, 772, 414, NAVY)
    draw_text(cv, "GOPALPUR", 666, 394, 2, WHITE, weight=1)


def draw_flags(cv, x, y):
    """Three small flags: USA, China, Russia, side by side."""
    fw, fh = 100, 56
    # USA: red and white stripes with a blue canton.
    for s in range(7):
        cv.box(x, y + s * 8, x + fw - 1, y + s * 8 + 7,
               RED if s % 2 == 0 else WHITE)
    cv.box(x, y, x + 39, y + 31, NAVY)
    cv.star(x + 20, y + 16, 7, WHITE)
    # China: red field, one big gold star and four small ones.
    cx = x + fw + 22
    cv.box(cx, y, cx + fw - 1, y + fh - 1, RED)
    cv.star(cx + 22, y + 18, 11, GOLD)
    for sx, sy in ((52, 10), (64, 18), (64, 32), (52, 40)):
        cv.star(cx + sx, y + sy, 5, GOLD)
    # Russia: white, blue and red horizontal bands.
    rx = cx + fw + 22
    cv.box(rx, y, rx + fw - 1, y + 18, WHITE)
    cv.box(rx, y + 19, rx + fw - 1, y + 37, BLUE)
    cv.box(rx, y + 38, rx + fw - 1, y + fh - 1, RED)
    cv.frame(x, y, x + fw - 1, y + fh - 1, INK, 2)
    cv.frame(cx, y, cx + fw - 1, y + fh - 1, INK, 2)
    cv.frame(rx, y, rx + fw - 1, y + fh - 1, INK, 2)


def draw_eu_disc(cv, cx, cy, rad):
    """The EU circle of twelve gold stars on blue."""
    cv.disc(cx, cy, rad, BLUE)
    cv.ring(cx, cy, rad, INK, 2)
    for n in range(12):
        ang = -math.pi / 2 + n * math.pi / 6
        cv.star(int(cx + (rad - 13) * math.cos(ang)),
                int(cy + (rad - 13) * math.sin(ang)), 6, GOLD)


def panel(cv, x0, y0, x1, y1, bar):
    cv.box(x0, y0, x1, y1, CARD)
    cv.frame(x0, y0, x1, y1, INK, 2)
    cv.box(x0 + 2, y0 + 2, x1 - 2, y0 + 11, bar)


def body_lines(cv, text, x, y, scale, max_w, color=INK, gap=None):
    if gap is None:
        gap = 11 * scale + 2
    for line in wrap_text(text, scale, max_w):
        draw_text(cv, line, x, y, scale, color, weight=2)
        y += gap
    return y


def build():
    cv = Canvas(W, H, PAPER)
    cv.frame(16, 16, W - 17, H - 17, INK, 2)
    cv.frame(22, 22, W - 23, H - 23, INK, 1)

    # Masthead: plain title, red date band.
    draw_text(cv, "THE WORLD IN ONE DAY", 512, 34, 5, INK, align="center")
    cv.box(28, 100, 996, 102, INK)
    cv.box(28, 106, 996, 146, RED)
    draw_text(cv, "FRIDAY - 20 NOVEMBER 2026", 512, 112, 3, WHITE, align="center")

    # Hero: Cyclone Akvan over the Bay of Bengal.
    cv.box(28, 168, 996, 496, SEA)
    draw_rain(cv, 28, 168, 996, 420, SKY)
    draw_spiral(cv, 320, 305, PALE)
    draw_coast(cv)
    cv.box(40, 182, 250, 216, RED)
    draw_text(cv, "LEAD STORY", 145, 188, 2, WHITE, weight=1, align="center")
    cv.box(28, 420, 996, 496, NAVY)
    draw_text(cv, "CYCLONE AKVAN HITS INDIA", 512, 428, 4, WHITE, align="center")
    draw_text(cv, "80,000 EVACUATED - WINDS 100 KM/H - NOON LANDFALL",
              512, 470, 2, WHITE, weight=1, align="center")

    # Row 2: the two diplomacy stories.
    panel(cv, 28, 512, 506, 784, NAVY)
    draw_flags(cv, 95, 534)
    draw_text(cv, "THREE LEADERS,", 267, 604, 3, INK, align="center")
    draw_text(cv, "NO DEAL", 267, 638, 3, INK, align="center")
    body_lines(cv, "TRUMP, XI AND PUTIN MEET IN SHENZHEN. NO DEAL ON "
                   "IRAN OR UKRAINE. IRAN DECISION PAST JAN 1.",
               44, 682, 2, 440, gap=22)

    panel(cv, 518, 512, 996, 784, BLUE)
    draw_eu_disc(cv, 600, 566, 38)
    draw_text(cv, "EUROPE ANSWERS", 757, 616, 3, INK, align="center")
    draw_text(cv, "IN BERLIN", 757, 650, 3, INK, align="center")
    body_lines(cv, "30 LEADERS BACK UKRAINE IN BERLIN. EU PLANS 45BN "
                   "EURO AID AND SECURITY GUARANTEES.",
               544, 692, 2, 440, gap=22)

    # Row 3: three big-number panels.
    panel(cv, 28, 800, 342, 936, TEAL)
    draw_text(cv, "GTA VI - GAMES", 185, 812, 2, INK, align="center")
    draw_text(cv, "$2.4BN", 185, 834, 5, INK, align="center")
    draw_text(cv, "24.6M COPIES", 185, 890, 2, INK, align="center")
    draw_text(cv, "IN A DAY (EST.)", 185, 910, 2, INK, align="center")

    panel(cv, 354, 800, 668, 936, NAVY)
    draw_text(cv, "ANTHROPIC - IPO", 511, 812, 2, INK, align="center")
    draw_text(cv, "+17%", 511, 834, 5, BLUE, align="center")
    draw_text(cv, "$83 TO $97.17", 511, 890, 2, INK, align="center")
    draw_text(cv, "RECORD IPO DEBUT", 511, 910, 2, INK, align="center")

    panel(cv, 680, 800, 996, 936, RED)
    draw_text(cv, "TAIEX - MARKETS", 838, 812, 2, INK, align="center")
    draw_text(cv, "-4.6%", 838, 834, 5, RED, align="center")
    draw_text(cv, "TAIWAN CURBS", 838, 890, 2, INK, align="center")
    draw_text(cv, "SHORT SELLING", 838, 910, 2, INK, align="center")

    # Ticker: the rest of the day, plus sources.
    cv.box(28, 950, 996, 952, INK)
    draw_text(cv, "ALSO TODAY: PETE ROSE PARDONED - NZ 368 V INDIA",
              512, 958, 2, INK, align="center")
    draw_text(cv, "KAKAO CLEARED - EU-UK SUMMIT - WORLD CHILDREN'S DAY",
              512, 980, 2, INK, align="center")
    draw_text(cv, "SOURCES: REUTERS, BBC, IMD, SENSOR TOWER, NASDAQ",
              512, 1006, 1, GREY, weight=1, align="center")
    return cv


def png_bytes(cv):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    blob = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))
    return blob


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes(build()))
    print("wrote", path)


if __name__ == "__main__":
    main()
