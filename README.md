# digital gecko

a custom [Iosevka](https://github.com/be5invis/Iosevka) typeface variant built for legibility, adaptability, readability, and accessibility.

## overview

this repository contains a specialized build of Iosevka designed specifically for use on my personal website. the variant emphasizes clear letterforms and carefully selected glyphs to ensure the font remains readable across different media, screen sizes, and accessibility contexts.

## design choices

the custom variant includes:

- **numerals**: slashed zero (more distinguishable), no-base one, flat-top three
- **letters**: sans-serif design with selective serifs on capitals for contrast
- **spacing**: normal monospace proportions for optimal web rendering
- **ligatures**: limited to discretionary ligatures for programming contexts
- **symbols**: compact at-sign and through dollar sign for clean appearance

the configuration is defined in `digitalgecko.toml` using Iosevka's build system.

## building locally

### prerequisites

- Node.js 18 or higher
- ttfautohint (for hinting)

on Debian/Ubuntu:
```bash
sudo apt-get install ttfautohint
```

on macOS with Homebrew:
```bash
brew install ttfautohint
```

### build steps

1. Clone this repository
2. Clone Iosevka into a temporary location:
```bash
git clone --depth 1 https://github.com/be5invis/Iosevka.git /tmp/Iosevka
cd /tmp/Iosevka
npm install
```

3. Copy the configuration:
```bash
cp /path/to/digital-gecko/digitalgecko.toml /tmp/Iosevka/private-build-plans.toml
```

4. Build the font:
```bash
npm run build -- contents::DigitalGecko
```

5. Find the built fonts in `/tmp/Iosevka/dist/`

## automated builds

this repository uses GitHub Actions to automatically build the font when the configuration changes. built artifacts are available in the Actions section of this repository.

## usage

install the built TTF or OTF files in your operating system's font directory, or embed them in your website using `@font-face` with the provided WOFF2 files.

## license

this project is a derivative work of [Iosevka](https://github.com/be5invis/Iosevka) and is licensed under the SIL Open Font License v1.1. see `LICENSE.md` for details.

built fonts may be freely used, modified, and redistributed under the terms of the SIL OFL.

## credits

designed with [Iosevka](https://github.com/be5invis/Iosevka) by Renzhi Li (Belleve Invis).
