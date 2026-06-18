# -*- coding: utf-8 -*-
"""Toz emme sistemi yerlesim plani icin basit semantik ikonlar (PIL ile)."""
from PIL import Image, ImageDraw
import math

OUT = "/home/user/St/icons"

NAVY = (31, 56, 100, 255)
BLUE = (46, 83, 149, 255)
GREY = (120, 120, 120, 255)
DGREY = (70, 70, 70, 255)
ORANGE = (200, 110, 30, 255)
TEAL = (30, 130, 120, 255)
TRANSP = (0, 0, 0, 0)


def new_img(w=120, h=120):
    return Image.new("RGBA", (w, h), TRANSP)


def save(img, name):
    img.save(f"{OUT}/{name}.png")


# ---------------- FAN ikonu ----------------
img = new_img(120, 120)
d = ImageDraw.Draw(img)
cx, cy, r = 60, 60, 50
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=6)
for ang in range(0, 360, 60):
    a = math.radians(ang)
    a2 = math.radians(ang + 35)
    x1, y1 = cx + 10 * math.cos(a), cy + 10 * math.sin(a)
    x2, y2 = cx + r * 0.78 * math.cos(a2), cy + r * 0.78 * math.sin(a2)
    d.line([x1, y1, x2, y2], fill=BLUE, width=8)
d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=NAVY)
save(img, "fan")

# ---------------- FILTRE ikonu (torba filtre) ----------------
img = new_img(120, 120)
d = ImageDraw.Draw(img)
d.rectangle([20, 10, 100, 80], outline=DGREY, width=6, fill=(235, 240, 245, 255))
for x in range(30, 100, 14):
    d.line([x, 16, x, 74], fill=TEAL, width=4)
d.polygon([(20, 80), (100, 80), (60, 112)], outline=DGREY, width=6, fill=(235, 240, 245, 255))
save(img, "filtre")

# ---------------- KOLON ikonu (yapi kolonu - cross-hatch kare) ----------------
img = new_img(80, 80)
d = ImageDraw.Draw(img)
d.rectangle([6, 6, 74, 74], outline=(0, 0, 0, 255), width=4, fill=(190, 190, 190, 255))
for i in range(-70, 80, 12):
    d.line([6 + max(i, 0), 6 + max(-i, 0), 74 + min(i, 0) - max(0, i - 68), 74], fill=GREY, width=2)
save(img, "kolon")

# ---------------- MAKINE ikonu ----------------
img = new_img(120, 90)
d = ImageDraw.Draw(img)
d.rectangle([6, 16, 114, 84], outline=DGREY, width=5, fill=(252, 228, 200, 255))
d.ellipse([46, 36, 74, 64], outline=ORANGE, width=5)
d.rectangle([6, 6, 30, 20], outline=DGREY, width=4, fill=(252, 228, 200, 255))
save(img, "makine")

# ---------------- ANA HAT BORU (legend - duz segment) ----------------
img = new_img(140, 40)
d = ImageDraw.Draw(img)
d.line([8, 20, 132, 20], fill=NAVY, width=12)
save(img, "boru_ana")

# ---------------- BRANSMAN BORU (legend - ince segment) ----------------
img = new_img(140, 40)
d = ImageDraw.Draw(img)
d.line([8, 20, 132, 20], fill=BLUE, width=7)
save(img, "boru_bransman")

# ---------------- DIRSEK (90 derece elbow) ----------------
img = new_img(100, 100)
d = ImageDraw.Draw(img)
d.line([15, 15, 15, 85], fill=BLUE, width=10)
d.line([15, 85, 85, 85], fill=BLUE, width=10)
save(img, "dirsek")

print("Ikonlar olusturuldu:", OUT)
