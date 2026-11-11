#!/usr/bin/env python3
"""Per-post social cards: the post headline on the brand background, 1200x630.

Called by blog/build.py. A post that still uses the default /og-image.jpg gets
/img/og/<slug>.jpg (Hebrew posts: /img/og/he-<slug>.jpg). A card is only redrawn when
its title changes (see manifest.json), so a rebuild of unchanged posts changes nothing.

Needs Pillow (python3 -m pip install pillow). Without it the build keeps the default image.
Fonts are in blog/fonts (Anton, Heebo, Space Grotesk, all SIL Open Font License).
"""
import hashlib
import json
import os

VERSION = "1"            # bump to redraw every card after a design change
W, H = 1200, 630
PAD = 84
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


def _font(name, size, weight=None):
    from PIL import ImageFont
    f = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def _background():
    from PIL import Image, ImageDraw, ImageFilter
    img = Image.new("RGB", (W, H), (6, 8, 12))
    glow = Image.new("RGB", (W, H), (6, 8, 12))
    d = ImageDraw.Draw(glow)
    d.ellipse((-260, -330, 760, 420), fill=(14, 52, 92))
    d.ellipse((760, 330, 1500, 900), fill=(10, 30, 54))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(150)), 0.9)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 8), fill=(90, 176, 255))
    return img


def _wrap(draw, text, font, max_w, rtl):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font, direction="rtl" if rtl else "ltr") <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _draw(title, he):
    from PIL import ImageDraw
    img = _background()
    d = ImageDraw.Draw(img)
    rtl = bool(he)
    direction = "rtl" if rtl else "ltr"
    max_w = W - 2 * PAD
    x = W - PAD if rtl else PAD
    anchor = "ra" if rtl else "la"

    # brand line
    brand = _font("Anton-Regular.ttf", 40)
    d.text((PAD, 62), "TAL PAPERIN", font=brand, fill=(255, 255, 255))
    sub = _font("SpaceGrotesk.ttf", 24, 600)
    d.text((W - PAD, 74), "FRACTIONAL CRO", font=sub, fill=(90, 176, 255), anchor="ra")

    # headline: largest size that fits in 4 lines
    lines, font, size = [], None, 0
    for size in (88, 80, 72, 64, 58, 52, 46, 42):
        font = _font("Heebo.ttf", int(size * 0.86), 800) if he else _font("Anton-Regular.ttf", size)
        lines = _wrap(d, title, font, max_w, rtl)
        if len(lines) <= 4 and len(lines) * int(size * (1.22 if he else 1.16)) <= 340:
            break
    if len(lines) > 5:
        lines = lines[:5]
        lines[-1] = lines[-1].rstrip(" ,.:;") + "..."
    lh = int(size * (1.22 if he else 1.16))
    block = lh * len(lines)
    y = 150 + max(0, (H - 150 - 110 - block) // 2)
    for ln in lines:
        d.text((x, y), ln, font=font, fill=(255, 255, 255), anchor=anchor, direction=direction)
        y += lh

    # footer
    d.rectangle((PAD, H - 96, PAD + 150, H - 92), fill=(90, 176, 255))
    foot = _font("SpaceGrotesk.ttf", 26, 600)
    d.text((PAD, H - 76), "talpaperin.com", font=foot, fill=(154, 167, 181))
    return img


def ensure_cards(posts, root):
    """Draw missing or outdated cards. Returns {(lang, slug): '/img/og/..jpg'} for cards on disk."""
    out_dir = os.path.join(root, "img", "og")
    mpath = os.path.join(out_dir, "manifest.json")
    try:
        import PIL  # noqa: F401
        have_pil = True
    except ImportError:
        have_pil = False
    manifest = {}
    if os.path.exists(mpath):
        with open(mpath, encoding="utf-8") as f:
            manifest = json.load(f)
    before = dict(manifest)
    result, wanted = {}, set()
    for p in posts:
        if p["image"] != "/og-image.jpg":
            continue
        he = p["lang"] == "he"
        key = ("he-" if he else "") + p["slug"]
        wanted.add(key)
        path = os.path.join(out_dir, key + ".jpg")
        h = hashlib.sha1((VERSION + "|" + p["title"]).encode("utf-8")).hexdigest()[:16]
        if have_pil and (manifest.get(key) != h or not os.path.exists(path)):
            os.makedirs(out_dir, exist_ok=True)
            _draw(p["title"], he).save(path, "JPEG", quality=72, optimize=True, progressive=True)
            manifest[key] = h
        if os.path.exists(path):
            result[(p["lang"], p["slug"])] = "/img/og/%s.jpg" % key
    if have_pil:
        # cards for posts that no longer exist (future-dated posts are kept: their keys are unknown here)
        pass
    if manifest != before:
        with open(mpath, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=0, sort_keys=True, ensure_ascii=False)
            f.write("\n")
    return result
