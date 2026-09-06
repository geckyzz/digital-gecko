#!/usr/bin/env python3
"""
Render banner, preview and pangram samples for README.
- 2× retina (scale=2)
- banner: 3200×452 with gray border, dark/light
- preview: 2080×2080 grid, baseline-aligned (anchor=ms), no outer border
- pangrams: borderless, minimal margins, 4 styles per language (Regular/Italic/Bold/Bold Italic)
Usage:
  python render.py --all
  python render.py banner preview pangram
  python render.py pangram --scale 2
Fonts: tries ./dist/ttf, ~/Git/rd/api/static/fonts, then system.
"""

import argparse
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
SRC.mkdir(exist_ok=True)

# Try to locate Digital Gecko fonts
CANDIDATE_DIRS = [
    ROOT / "dist" / "ttf",
    ROOT / "dist" / "woff2",
    pathlib.Path.home() / "Git/rd/api/static/fonts",
    pathlib.Path("~/Git/rd/api/static/fonts").expanduser(),
    pathlib.Path("/tmp/Iosevka/dist/DigitalGecko/TTF"),
]


def find_font(name: str) -> pathlib.Path:
    for d in CANDIDATE_DIRS:
        if not d.exists():
            continue
        # try exact woff2 or ttf
        for ext in [".woff2", ".ttf", ".otf"]:
            p = d / f"{name}{ext}"
            if p.exists():
                return p
            # case: Digital-Gecko-Bold.woff2 vs DigitalGecko-Bold.ttf from build
            alt = (
                d / f"DigitalGecko-{name.split('-', 1)[-1]}{ext}"
                if "-" in name
                else None
            )
            if alt and alt.exists():
                return alt
        # glob
        for p in d.glob(f"*{name.split('-')[-1]}*"):
            if p.suffix in (".woff2", ".ttf", ".otf"):
                return p
    # fallback to ~/Git/rd
    return pathlib.Path.home() / f"Git/rd/api/static/fonts/{name}.woff2"


NAMES = {
    "regular": "Digital-Gecko",
    "italic": "Digital-Gecko-Italic",
    "bold": "Digital-Gecko-Bold",
    "bolditalic": "Digital-Gecko-Bold-Italic",
    "extrabold": "Digital-Gecko-ExtraBold",
}


def load(size: int, key: str) -> ImageFont.FreeTypeFont:
    name = NAMES.get(key, key)
    p = find_font(name)
    if not p.exists():
        # try ~/Git/rd directly
        p = pathlib.Path.home() / f"Git/rd/api/static/fonts/{name}.woff2"
    return ImageFont.truetype(str(p), size)


W_BANNER = 1600
CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;!?'\"()[]{}<>@#$%^&*+-=/_\\|~`"
PANGRAMS = [
    ("en", "English", "The quick brown fox jumps over the lazy dog"),
    (
        "id",
        "Bahasa Indonesia / Melayu",
        "Muharjo seorang xenofobia universal yang takut pada warga jazirah, contohnya Qatar.",
    ),
    ("ru", "Русский", "Съешь ещё этих мягких французских булок, да выпей же чаю"),
    ("el", "Ελληνικά", "Γαζέες καὶ μυρτιὲς δὲν θὰ βρῶ πιὰ στὸ χρυσαφὶ ξέφωτο"),
]

SOCIAL_SIZES = [
    (1280, 640),
    (2560, 1280),
]  # 1× and 2× for best display (GitHub recommends 1280×640)


def render_banner(scale=2):
    W = W_BANNER * scale
    pad_x = 72 * scale
    pad_top = 44 * scale
    pad_bottom = 44 * scale
    border_w = 2 * scale
    BG, BORDER, TEXT, SUB = "#121212", "#808080", "#FFFFFF", "#9FA0A3"
    BG_L, BORDER_L = "#F5F5F5", "#CCCCCC"
    font_h1 = load(72 * scale, "extrabold")
    font_sub = load(24 * scale, "regular")
    subtitle = "a custom Iosevka typeface variant built for legibility, adaptability, readability, and accessibility."
    tmp = Image.new("RGB", (W, 100), BG)
    d = ImageDraw.Draw(tmp)

    def wrap(text, font, max_w):
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = cur + (" " if cur else "") + w
            if d.textbbox((0, 0), test, font=font)[2] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    avail = W - pad_x * 2
    lines = wrap(subtitle, font_sub, avail)
    H = pad_top + 88 * scale + 18 * scale + len(lines) * 32 * scale + pad_bottom
    H = int(H)
    for is_light, bg, border, text, sub in [
        (False, BG, BORDER, TEXT, SUB),
        (True, BG_L, BORDER_L, "#000000", "#6A6A6A"),
    ]:
        img = Image.new("RGB", (W, H), border)
        inner = Image.new("RGB", (W - border_w * 2, H - border_w * 2), bg)
        img.paste(inner, (border_w, border_w))
        draw = ImageDraw.Draw(img)
        ox, oy = border_w, border_w
        y = pad_top + oy
        draw.text((pad_x + ox, y), "Digital Gecko", font=font_h1, fill=text)
        y += 88 * scale + 18 * scale
        for line in lines:
            draw.text((pad_x + ox, y), line, font=font_sub, fill=sub)
            y += 32 * scale
        out = SRC / f"{'banner-light.png' if is_light else 'banner.png'}"
        img.save(out)
        print(f"banner {out} {W}x{H}")


def render_preview(scale=2):
    cols = 10
    cell_w, cell_h = 100 * scale, 100 * scale
    font_size = 48 * scale
    label_size = 11 * scale
    pad = 20 * scale
    BG = "#121212"
    GRID = "#2A2A2E"
    TEXT = "#FFFFFF"
    MUTED = "#5A5C60"
    BG_L = "#F5F5F5"
    GRID_L = "#E0E0E0"
    font = load(font_size, "regular")
    font_label = load(label_size, "regular")
    ascent, descent = font.getmetrics()
    rows = (len(CHARSET) + cols - 1) // cols
    img_w = cols * cell_w + pad * 2
    img_h = rows * cell_h + pad * 2
    for is_light, bg, grid, text, muted in [
        (False, BG, GRID, TEXT, MUTED),
        (True, BG_L, GRID_L, "#000000", "#9AA0A6"),
    ]:
        img = Image.new("RGB", (img_w, img_h), bg)
        draw = ImageDraw.Draw(img)
        for idx, ch in enumerate(CHARSET):
            r = idx // cols
            c = idx % cols
            x0 = pad + c * cell_w
            y0 = pad + r * cell_h
            draw.rectangle(
                [x0, y0, x0 + cell_w, y0 + cell_h],
                outline=grid,
                width=max(1, scale // 2),
            )
            cx = x0 + cell_w // 2
            baseline_y = y0 + (cell_h - (ascent + descent)) // 2 + ascent
            draw.text((cx, baseline_y), ch, fill=text, font=font, anchor="ms")
            draw.text(
                (x0 + cell_w // 2, y0 + cell_h - 13 * scale),
                ch,
                fill=muted,
                font=font_label,
                anchor="mm",
            )
        out = SRC / f"{'preview-light.png' if is_light else 'preview.png'}"
        img.save(out)
        print(f"preview {out} {img_w}x{img_h}")


def render_social():
    # GitHub social preview: 1280×640 and 2560×1280 (2×), 40pt safe border, centered bigger type
    for W, H in SOCIAL_SIZES:
        BG = "#121212"
        pad = 40 * (W // 1280)
        img = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        scale = W / 1280
        font_title = load(int(96 * scale), "extrabold")
        font_sub = load(int(24 * scale), "regular")
        font_small = load(int(11 * scale), "regular")
        font_faint = load(int(200 * scale), "regular")
        font_faint_top = load(int(170 * scale), "italic")  # 0.85× faint, italic, more dim
        title = "Digital Gecko"
        subtitle_lines = [
            "a custom Iosevka typeface variant",
            "legible // adaptable // readable // accessible",
        ]
        footer = (
            "TTF, WOFF2, TTC // SIL OFL // 7562 glyphs // latin, cyrillic, greek"
        )
        tb = draw.textbbox((0, 0), title, font=font_title)
        title_h = tb[3] - tb[1]
        sb0 = draw.textbbox((0, 0), subtitle_lines[0], font=font_sub)
        sub_h = sb0[3] - sb0[1]
        gap = int(24 * scale)
        sub_gap = int(8 * scale)
        block_h = title_h + gap + sub_h * len(subtitle_lines) + sub_gap * (len(subtitle_lines) - 1)
        center_y = H // 2
        title_y = center_y - block_h // 2 + title_h // 2
        # faint — bottom left 0px, Xi for greek, anchor similar to preview (ms/ls with baseline)
        # use ls (left, s) to include descender like preview's ms, 0px at canvas edge
        for txt, xoff in [("Aa", 0), ("Гг", 320 * scale), ("Ξξ", 640 * scale)]:
            draw.text(
                (xoff, H),
                txt,
                font=font_faint,
                fill="#1E1E1E",
                anchor="ls",
            )
        # faint Digital Gecko — top right, right-aligned, slightly cropped, 0.85× faint, dim italic, more dim
        draw.text(
            (W, -6 * scale),
            title,
            font=font_faint_top,
            fill="#141414",
            anchor="rt",
        )
        # main content — centered, bigger
        draw.text((W // 2, title_y), title, font=font_title, fill="#FFFFFF", anchor="mm")
        sub_y0 = title_y + title_h // 2 + gap + sub_h // 2
        for i, line in enumerate(subtitle_lines):
            y = sub_y0 + i * (sub_h + sub_gap)
            draw.text((W // 2, y), line, font=font_sub, fill="#9FA0A3", anchor="mm")
        draw.text(
            (W // 2, H - pad - 12 * scale),
            footer,
            font=font_small,
            fill="#5A5C60",
            anchor="mm",
        )
        suffix = "" if W == 1280 else "-2x"
        out = SRC / f"social-preview{suffix}.png"
        img.save(out)
        print(f"social {out} {W}x{H}")


def render_pangrams(scale=2):
    W = 1600 * scale
    # dropped margins: minimal padding
    pad_x = 32 * scale
    styles = [
        ("Regular", "regular"),
        ("Italic", "italic"),
        ("Bold", "bold"),
        ("Bold Italic", "bolditalic"),
    ]
    for code, lang, pangram in PANGRAMS:
        for is_light, bg, text, muted in [
            (False, "#121212", "#FFFFFF", "#5A5C60"),
            (True, "#F5F5F5", "#000000", "#9AA0A6"),
        ]:
            font_label = load(12 * scale, "bold")
            # wrap using bold (widest) to ensure all fit
            tmp = Image.new("RGB", (W, 100), bg)
            d = ImageDraw.Draw(tmp)
            font_wrap = load(28 * scale, "bold")

            def wrap2(txt, font, max_w, d=d):
                words = txt.split()
                lines = []
                cur = ""
                for w in words:
                    test = cur + (" " if cur else "") + w
                    if d.textbbox((0, 0), test, font=font)[2] <= max_w:
                        cur = test
                    else:
                        if cur:
                            lines.append(cur)
                        cur = w
                if cur:
                    lines.append(cur)
                return lines

            avail = W - pad_x * 2
            p_lines = wrap2(pangram, font_wrap, avail)
            n_style = len(styles)
            style_h = 18 * scale + len(p_lines) * 36 * scale + 12 * scale
            H = 28 * scale + n_style * style_h + 16 * scale
            img = Image.new("RGB", (W, H), bg)  # no outer border, dropped margins
            draw = ImageDraw.Draw(img)
            y = 16 * scale
            draw.text((pad_x, y), lang.upper(), font=font_label, fill=muted)
            draw.text(
                (
                    pad_x
                    + draw.textbbox((0, 0), lang.upper(), font=font_label)[2]
                    + 12 * scale,
                    y,
                ),
                "— pangram",
                font=load(11 * scale, "regular"),
                fill=muted,
            )
            y += 28 * scale
            for style_name, key in styles:
                font_slabel = load(10 * scale, "regular")
                draw.text((pad_x, y), style_name.upper(), font=font_slabel, fill=muted)
                y += 14 * scale
                font_p = load(26 * scale, key)
                # re-wrap per actual font
                p_lines_actual = wrap2(pangram, font_p, avail)
                for line in p_lines_actual:
                    draw.text((pad_x, y), line, font=font_p, fill=text)
                    y += 32 * scale
                y += 12 * scale
            out = SRC / f"sample-{code}{'-light' if is_light else ''}.png"
            img.save(out)
            print(f"pangram {out} {W}x{H} {code}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "targets",
        nargs="*",
        default=["all"],
        choices=["all", "banner", "preview", "pangram", "social"],
    )
    p.add_argument("--all", action="store_true", help="render all (alias)")
    p.add_argument("--scale", type=int, default=2, help="retina scale, default 2")
    args = p.parse_args()
    t = set(args.targets)
    if args.all or "all" in t or not t:
        t = {"banner", "preview", "pangram", "social"}
    if "banner" in t:
        render_banner(scale=args.scale)
    if "preview" in t:
        render_preview(scale=args.scale)
    if "pangram" in t:
        render_pangrams(scale=args.scale)
    if "social" in t:
        render_social()
