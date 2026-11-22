# Recolours the BKBoK banner for a honey (#ffc30b-ish) header.
import sys
from PIL import Image
src, dst, height = sys.argv[1], sys.argv[2], int(sys.argv[3])
KEYS = [  # old colour -> new colour
    ((128, 96, 1),   (59, 37, 0)),     # lettering: olive brown -> dark honey brown
    ((252, 250, 240),(255, 248, 225)), # book pages
    ((242, 233, 211),(250, 232, 180)), # page shading
    ((255, 255, 255),(255, 252, 238)), # wings
    ((0, 0, 0),      (32, 20, 0)),     # bee
    ((153, 87, 69),  (122, 61, 18)),   # book cover
    ((159, 135, 77), (150, 105, 30)),
    ((236, 231, 220),(245, 228, 185)),
]
im = Image.open(src).convert("RGBA")
px = im.load()
cache = {}
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = px[x, y]
        if a == 0: continue
        k = (r, g, b)
        if k not in cache:
            old, new = min(KEYS, key=lambda kv: sum((p - q) ** 2 for p, q in zip(k, kv[0])))
            cache[k] = tuple(max(0, min(255, n + (p - o))) for p, o, n in zip(k, old, new))
        px[x, y] = cache[k] + (a,)
im.save(dst.replace(".png", "-full.png"))
w = round(im.width * height / im.height)
im.resize((w, height), Image.LANCZOS).save(dst, optimize=True)
