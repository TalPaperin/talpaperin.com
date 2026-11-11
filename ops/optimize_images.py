#!/usr/bin/env python3
"""Make light WebP copies of the site's images and record their dimensions.

Run after adding or replacing a logo, a testimonial photo or a page photo:
    python3 -m pip install pillow
    python3 ops/optimize_images.py
then rebuild (services/build.py, blog/build.py).

The .jpg originals stay (structured data and social cards still point at them). The build
reads img/dims.json and, where a WebP copy exists, links it and writes width and height
into the <img> tag so the page does not jump while images load.
"""
import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# folder -> (max width, max height, quality)
RULES = {
    "logos": (520, 172, 84),            # shown at 40 to 86px high
    "img/testimonials": (132, 132, 82),  # shown at 44 to 50px
    "img/site": (1280, 1400, 78),
}


def main():
    dims_path = os.path.join(ROOT, "img", "dims.json")
    dims = {}
    made = 0
    for folder, (mw, mh, q) in RULES.items():
        d = os.path.join(ROOT, folder)
        for fn in sorted(os.listdir(d)):
            if not fn.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            src = os.path.join(d, fn)
            out = os.path.splitext(src)[0] + ".webp"
            if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
                im = Image.open(src)
                im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
                im.thumbnail((mw, mh), Image.LANCZOS)
                im.save(out, "WEBP", quality=q, method=6)
                made += 1
            with Image.open(out) as o:
                dims["/" + os.path.relpath(out, ROOT).replace(os.sep, "/")] = list(o.size)
    # hero images already ship as WebP
    for fn in sorted(os.listdir(os.path.join(ROOT, "img", "site"))):
        if fn.endswith(".webp"):
            with Image.open(os.path.join(ROOT, "img", "site", fn)) as o:
                dims["/img/site/" + fn] = list(o.size)
    with open(dims_path, "w", encoding="utf-8") as f:
        json.dump(dims, f, indent=0, sort_keys=True)
        f.write("\n")
    print("WebP copies written: %d, dimensions recorded: %d" % (made, len(dims)))


if __name__ == "__main__":
    main()
