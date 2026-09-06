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
Fonts: tries ./dist/ttf, ~/Git/website/api/static/fonts (legacy rd path), then system.
"""

import argparse
import pathlib

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
SRC.mkdir(exist_ok=True)

# font search order: local dist → rd → tmp builds
CANDIDATE_DIRS = [
    ROOT / "dist" / "ttf",
    ROOT / "dist" / "woff2",
    pathlib.Path.home() / "Git/rd/api/static/fonts",
    pathlib.Path("~/Git/rd/api/static/fonts").expanduser(),
    pathlib.Path("/tmp/dg"),
    pathlib.Path("/tmp/Iosevka/dist/DigitalGecko/TTF"),
]


def find_font(name: str) -> pathlib.Path:
    # exact + hyphen-swapped only; avoid glob that confuses Thin/ThinItalic
    variants = {
        name,
        name.replace("Digital-Gecko", "DigitalGecko"),
        name.replace("DigitalGecko", "Digital-Gecko"),
    }
    for d in CANDIDATE_DIRS:
        if not d.exists():
            continue
        for v in variants:
            for ext in [".woff2", ".ttf", ".otf"]:
                p = d / f"{v}{ext}"
                if p.exists():
                    return p
    return pathlib.Path.home() / f"Git/rd/api/static/fonts/{name}.woff2"


NAMES = {
    "regular": "Digital-Gecko",
    "italic": "Digital-Gecko-Italic",
    "bold": "Digital-Gecko-Bold",
    "bolditalic": "Digital-Gecko-Bold-Italic",
    "extrabold": "Digital-Gecko-ExtraBold",
    "extrabolditalic": "Digital-Gecko-ExtraBold-Italic",
    "thin": "DigitalGecko-ExtendedThin",
    "thinitalic": "DigitalGecko-ExtendedThinItalic",
    "extended": "DigitalGecko-Extended",
    "extendeditalic": "DigitalGecko-ExtendedItalic",
    "extendedextrabold": "DigitalGecko-ExtendedExtraBold",
    "extendedextrabolditalic": "DigitalGecko-ExtendedExtraBoldItalic",
}


def load(size: int, key: str) -> ImageFont.FreeTypeFont:
    name = NAMES.get(key, key)
    p = find_font(name)
    if not p.exists():
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
]


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
        base = Image.new("RGB", (W, H), border)
        base.paste(
            Image.new("RGB", (W - border_w * 2, H - border_w * 2), bg),
            (border_w, border_w),
        )
        # banner faint text: weight increases left→right (Thin→Heavy), static 3% opacity
        # sliced per-char with anchor rb + mask to preserve kerning/shaping
        faint_text = "Digital Gecko"
        faint_size = int(H * 0.65)
        faint_keys = [
            "DigitalGecko-ExtendedThin",
            "DigitalGecko-ExtendedExtraLight",
            "DigitalGecko-ExtendedLight",
            "DigitalGecko-Extended",
            "DigitalGecko-ExtendedMedium",
            "DigitalGecko-ExtendedSemiBold",
            "DigitalGecko-ExtendedBold",
            "DigitalGecko-ExtendedExtraBold",
            "DigitalGecko-ExtendedHeavy",
        ]
        faint_fonts: list[ImageFont.FreeTypeFont] = []
        for k in faint_keys:
            try:
                faint_fonts.append(ImageFont.truetype(str(find_font(k)), faint_size))
            except OSError:
                faint_fonts.append(load(faint_size, "thin"))
        n = len(faint_text)
        char_wi: list[int | None] = []
        for i, ch in enumerate(faint_text):
            if ch == " ":
                char_wi.append(None)
            else:
                t = i / max(1, n - 1)
                wi = round(t * (len(faint_fonts) - 1))
                char_wi.append(wi)
        txt_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)
        base_fill = (255, 255, 255, 255) if not is_light else (0, 0, 0, 255)
        # use textlength for precise advance; total_w keeps right edge at W
        total_w = sum(
            txt_draw.textlength(
                ch,
                font=faint_fonts[len(faint_fonts) // 2]
                if wi is None
                else faint_fonts[wi],
            )
            for ch, wi in zip(faint_text, char_wi)
        )
        slice_bounds: list[tuple[float, float]] = []
        x0 = W - total_w
        cur = x0
        for ch, wi in zip(faint_text, char_wi):
            f = faint_fonts[len(faint_fonts) // 2] if wi is None else faint_fonts[wi]
            adv = txt_draw.textlength(ch, font=f)
            slice_bounds.append((cur, cur + adv))
            cur += adv
        # draw whole string per weight and mask to its slice
        for wi, (left_s, right_s) in zip(char_wi, slice_bounds):
            f = faint_fonts[len(faint_fonts) // 2] if wi is None else faint_fonts[wi]
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            ld.text((W, H), faint_text, font=f, fill=base_fill, anchor="rb")
            mask = Image.new("L", (W, H), 0)
            ImageDraw.Draw(mask).rectangle([int(left_s), 0, int(right_s), H], fill=255)
            alpha = layer.split()[3]
            masked = ImageChops.multiply(alpha, mask)
            layer.putalpha(masked)
            txt_layer = Image.alpha_composite(txt_layer, layer)
        # static 3% dim
        alpha_ch = txt_layer.split()[3]
        static_alpha = int(255 * 0.02)
        new_alpha = alpha_ch.point(lambda p, s=static_alpha: (p * s) // 255)
        txt_layer.putalpha(new_alpha)
        base_rgba = base.convert("RGBA")
        base_rgba = Image.alpha_composite(base_rgba, txt_layer)
        img = base_rgba.convert("RGB")
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
    # charset grid: baseline-aligned (anchor ms), no outer border
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
    # GitHub social preview: 1280x640 (2560x1280 @2x), centered type
    W2, H2 = 2560, 1280
    W1, H1 = 1280, 640
    BG = "#121212"
    scale = W2 / 1280
    img2 = Image.new("RGB", (W2, H2), BG)
    draw = ImageDraw.Draw(img2)
    font_title = load(int(96 * scale), "extrabold")
    font_sub = load(int(24 * scale), "regular")
    font_small = load(int(11 * scale), "regular")
    font_faint = load(int(200 * scale), "regular")
    font_faint_top = load(int(170 * scale), "italic")
    title = "Digital Gecko"
    subtitle_lines = [
        "a custom Iosevka typeface variant",
        "legible // adaptable // readable // accessible",
    ]
    footer = "TTF, WOFF2, TTC // SIL OFL // 7562 glyphs // latin, cyrillic, greek"
    pad2 = 40 * (W2 // 1280)
    tb = draw.textbbox((0, 0), title, font=font_title)
    title_h = tb[3] - tb[1]
    sb0 = draw.textbbox((0, 0), subtitle_lines[0], font=font_sub)
    sub_h = sb0[3] - sb0[1]
    gap = int(24 * scale)
    sub_gap = int(8 * scale)
    block_h = (
        title_h
        + gap
        + sub_h * len(subtitle_lines)
        + sub_gap * (len(subtitle_lines) - 1)
    )
    center_y = H2 // 2
    title_y = center_y - block_h // 2 + title_h // 2
    for txt, xoff in [("Aa", 0), ("Гг", 320 * scale), ("Ξξ", 640 * scale)]:
        draw.text((xoff, H2), txt, font=font_faint, fill="#1E1E1E", anchor="ls")
    draw.text((W2, -6 * scale), title, font=font_faint_top, fill="#141414", anchor="rt")
    draw.text((W2 // 2, title_y), title, font=font_title, fill="#FFFFFF", anchor="mm")
    sub_y0 = title_y + title_h // 2 + gap + sub_h // 2
    for i, line in enumerate(subtitle_lines):
        y = sub_y0 + i * (sub_h + sub_gap)
        draw.text((W2 // 2, y), line, font=font_sub, fill="#9FA0A3", anchor="mm")
    draw.text(
        (W2 // 2, H2 - pad2 - 12 * scale),
        footer,
        font=font_small,
        fill="#5A5C60",
        anchor="mm",
    )
    out2 = SRC / "social-preview-2x.png"
    img2.save(out2)
    print(f"social {out2} {W2}x{H2}")
    img1 = img2.resize((W1, H1), Image.LANCZOS)
    out1 = SRC / "social-preview.png"
    img1.save(out1)
    print(f"social {out1} {W1}x{H1} (downscaled from 2x)")


def render_preview_weights(scale=2):
    # weights showcase: 9 Extended weights × upright+italic
    W = 1600 * scale
    pad_x = 32 * scale
    weights_ext = [
        (
            "Thin",
            "DigitalGecko-ExtendedThin.woff2",
            "DigitalGecko-ExtendedThinItalic.woff2",
        ),
        (
            "ExtraLight",
            "DigitalGecko-ExtendedExtraLight.woff2",
            "DigitalGecko-ExtendedExtraLightItalic.woff2",
        ),
        (
            "Light",
            "DigitalGecko-ExtendedLight.woff2",
            "DigitalGecko-ExtendedLightItalic.woff2",
        ),
        ("Regular", "DigitalGecko-Extended.woff2", "DigitalGecko-ExtendedItalic.woff2"),
        (
            "Medium",
            "DigitalGecko-ExtendedMedium.woff2",
            "DigitalGecko-ExtendedMediumItalic.woff2",
        ),
        (
            "SemiBold",
            "DigitalGecko-ExtendedSemiBold.woff2",
            "DigitalGecko-ExtendedSemiBoldItalic.woff2",
        ),
        (
            "Bold",
            "DigitalGecko-ExtendedBold.woff2",
            "DigitalGecko-ExtendedBoldItalic.woff2",
        ),
        (
            "ExtraBold",
            "DigitalGecko-ExtendedExtraBold.woff2",
            "DigitalGecko-ExtendedExtraBoldItalic.woff2",
        ),
        (
            "Heavy",
            "DigitalGecko-ExtendedHeavy.woff2",
            "DigitalGecko-ExtendedHeavyItalic.woff2",
        ),
    ]
    for is_light, bg, text, muted, sub in [
        (False, "#121212", "#FFFFFF", "#5A5C60", "#9FA0A3"),
        (True, "#F5F5F5", "#000000", "#9AA0A6", "#8A8A8A"),
    ]:
        H_est = 1400 * scale
        img = Image.new("RGB", (W, H_est), bg)
        draw = ImageDraw.Draw(img)
        y = 24 * scale
        draw.text(
            (pad_x, y), "WEIGHTS".upper(), font=load(12 * scale, "bold"), fill=muted
        )
        y += 22 * scale
        draw.text(
            (pad_x, y),
            "9 weights × upright + italic",
            font=load(11 * scale, "regular"),
            fill=muted,
        )
        y += 24 * scale
        draw.line(
            [(pad_x, y), (W - pad_x, y)], fill="#2A2A2E" if not is_light else "#E0E0E0"
        )
        y += 16 * scale
        for weight_name, upright_file, italic_file in weights_ext:
            try:
                font_u = ImageFont.truetype(
                    str(find_font(upright_file.replace(".woff2", ""))), 26 * scale
                )
            except OSError:
                font_u = load(26 * scale, "regular")
            try:
                font_i = ImageFont.truetype(
                    str(find_font(italic_file.replace(".woff2", ""))), 26 * scale
                )
            except OSError:
                font_i = load(26 * scale, "italic")
            label_font = load(10 * scale, "regular")
            draw.text((pad_x, y), weight_name.upper(), font=label_font, fill=muted)
            y += 14 * scale
            pangram = "The quick brown fox jumps over the lazy dog — 0123456789"
            draw.text((pad_x, y), pangram, font=font_u, fill=text)
            y += 30 * scale
            draw.text((pad_x, y), pangram, font=font_i, fill=sub)
            y += 30 * scale
            y += 8 * scale
        H = y + 24 * scale
        img = img.crop((0, 0, W, H))
        out = SRC / f"preview-weights{'-light' if is_light else ''}.png"
        img.save(out)
        print(f"preview-weights {out} {W}x{H}")


def render_pangrams(scale=2):
    # pangram samples: borderless, 4 styles per language
    W = 1600 * scale
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
            img = Image.new("RGB", (W, H), bg)
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
        choices=[
            "all",
            "banner",
            "preview",
            "pangram",
            "social",
            "weights",
            "preview-weights",
        ],
    )
    p.add_argument("--all", action="store_true", help="render all (alias)")
    p.add_argument("--scale", type=int, default=2, help="retina scale, default 2")
    args = p.parse_args()
    t = set(args.targets)
    if args.all or "all" in t or not t:
        t = {"banner", "preview", "pangram", "social", "weights"}
    if "banner" in t:
        render_banner(scale=args.scale)
    if "preview" in t:
        render_preview(scale=args.scale)
    if "pangram" in t:
        render_pangrams(scale=args.scale)
    if "social" in t:
        render_social()
    if "weights" in t or "preview-weights" in t:
        render_preview_weights(scale=args.scale)
