#!/usr/bin/env python3
"""Build the BlueGreen website.

    templates/   page layouts (HTML) with {{keys}} where the texts go
    content/     all texts, English and Bangla side by side, plus site-wide values
    static/      style sheet, script, logo and images (copied as they are)
    _site/       the finished website (created by this script, published by GitHub)

Run it with:  python3 build_site.py
GitHub does this by itself every time a file is saved (see .github/workflows/deploy.yml).
Only the Python standard library is used.
"""
import html
import os
import re
import shutil
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(ROOT, "templates")
CONTENT = os.path.join(ROOT, "content")
STATIC = os.path.join(ROOT, "static")
OUT = os.path.join(ROOT, "_site")

ENGLISH_ONLY = {"404"}                                   # pages that exist only in English
DIGIT_SETTINGS = {"phone", "whatsapp_show", "licence_no"}  # shown with Bangla digits on Bangla pages
TOKEN = re.compile(r"(<!--.*?-->|<[^>]+>)", re.S)
LETTERS = re.compile(r"[A-Za-z]")
DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
BN_FONTS = "&family=Noto+Sans+Bengali:wght@400;500;600;700&family=Noto+Serif+Bengali:wght@500;600&display=swap"


class BuildError(Exception):
    pass


# --------------------------------------------------------------------------- reading files
def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_content(path):
    """content/<page>.txt  ->  {key: {'en': ..., 'bn': ...}}"""
    entries, key = {}, None
    for n, line in enumerate(read(path).splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = re.fullmatch(r"\[([^\]]+)\]", s)
        if m:
            key = m.group(1)
            if key in entries:
                raise BuildError(f"{os.path.basename(path)} line {n}: the name [{key}] appears twice")
            entries[key] = {}
            continue
        m = re.match(r"(en|bn):(.*)$", s)
        if m and key:
            entries[key][m.group(1)] = m.group(2).strip(" \t")
            continue
        raise BuildError(f"{os.path.basename(path)} line {n}: cannot understand this line: {s[:70]!r}\n"
                         "   (every text must be one line that starts with 'en:' or 'bn:' under its [name])")
    return entries


def read_settings(path):
    values = {}
    for n, line in enumerate(read(path).splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r"([a-z0-9_]+):\s*(.*)$", s)
        if not m:
            raise BuildError(f"_site.txt line {n}: cannot understand this line: {s[:70]!r}")
        values[m.group(1)] = m.group(2).strip()
    return values


# --------------------------------------------------------------------------- assembling a page
def assemble(slug, partials, svgs):
    """Join the page with head/header/footer and resolve everything that does not depend on language."""
    text = read(os.path.join(TEMPLATES, slug + ".html"))
    extra = ""
    m = re.search(r"\{\{#extra_head\}\}(.*?)\{\{/extra_head\}\}", text, re.S)
    if m:
        extra = m.group(1).strip("\n")
        text = text.replace(m.group(0), "")

    def include(m):
        if m.group(1) not in partials:
            raise BuildError(f"templates/{slug}.html: unknown {{{{include {m.group(1)}}}}}")
        return partials[m.group(1)].rstrip("\n")
    text = re.sub(r"^[ \t]*\{\{include (\w+)\}\}[ \t]*$", include, text, flags=re.M)
    text = text.replace("{{extra_head}}", extra)
    text = re.sub(r"\{\{!.*?!\}\}\n?", "", text, flags=re.S)   # notes for people who read the template

    flags = {"is_404": slug == "404"}
    text = re.sub(r"\{\{#if (\w+)\}\}(.*?)\{\{/if\}\}", lambda m: m.group(2) if flags.get(m.group(1)) else "", text, flags=re.S)
    text = re.sub(r"\{\{#unless (\w+)\}\}(.*?)\{\{/unless\}\}", lambda m: "" if flags.get(m.group(1)) else m.group(2), text, flags=re.S)

    home = slug in ("index", "404")
    text = text.replace("{{page_path}}", "" if slug == "index" else slug)
    text = text.replace("{{self_url}}", "./" if home else slug)
    text = text.replace("{{bn_url}}", "bn/" if home else "bn/" + slug)
    text = re.sub(r"\{\{here:(\w+)\}\}", lambda m: ' aria-current="page"' if m.group(1) == slug else "", text)

    def svg(m):
        if m.group(1) not in svgs:
            raise BuildError(f"templates/{slug}.html: no picture file templates/_svg/{m.group(1)}.svg")
        return svgs[m.group(1)]
    return re.sub(r"\{\{svg:([\w-]+)\}\}", svg, text)


# --------------------------------------------------------------------------- filling in the texts
class Texts:
    def __init__(self, page, shared, settings, lang, problems):
        self.page, self.shared, self.settings, self.lang, self.problems = page, shared, settings, lang, problems
        self.used = set()

    def setting(self, name, as_text):
        if name not in self.settings:
            raise BuildError(f"content/_site.txt has no value called '{name}'")
        v = self.settings[name]
        if as_text and self.lang == "bn" and name in DIGIT_SETTINGS:
            v = v.translate(DIGITS)
        return v

    def get(self, key, as_text):
        entry = self.page.get(key)
        if entry is None:
            entry = self.shared.get(key)
        if entry is None:
            raise BuildError(f"the text [{key}] is used in a template but is missing from the content files")
        self.used.add(key)
        value = entry.get(self.lang, "")
        if not value:
            value = entry.get("en", "")
            if self.lang == "bn" and value and key not in self.problems:
                self.problems.add(key)
        return re.sub(r"\{\{@([a-z0-9_]+)\}\}", lambda m: self.setting(m.group(1), as_text), value)


PH = re.compile(r"\{\{([~@]?)([^{}\s]+)\}\}")


def digits_outside_entities(s):
    return re.sub(r"(&#?\w+;)|(\d)", lambda m: m.group(1) or m.group(2).translate(DIGITS), s)


def fill(text, tx):
    out, skip = [], 0
    for tok in TOKEN.split(text):
        if not tok:
            continue
        if tok.startswith("<!--"):
            out.append(tok)
        elif tok.startswith("<"):
            low = tok.lower()
            if re.match(r"<(script|style|svg)\b", low) and not low.endswith("/>"):
                skip += 1
            elif re.match(r"</(script|style|svg)>", low):
                skip -= 1

            def in_tag(m):
                mode, name = m.groups()
                if mode == "@":
                    return html.escape(tx.setting(name, False), quote=True)
                if mode == "~":
                    return urllib.parse.quote(tx.get(name, False))
                return html.escape(tx.get(name, False), quote=True)
            out.append(PH.sub(in_tag, tok))
        elif skip:
            out.append(PH.sub(lambda m: tx.setting(m.group(2), False) if m.group(1) == "@" else m.group(0), tok))
        else:
            def in_text(m):
                mode, name = m.groups()
                if mode == "@":
                    return html.escape(tx.setting(name, True), quote=False)
                if mode == "~":
                    raise BuildError(f"{{{{~{name}}}}} can only be used inside a link")
                return html.escape(tx.get(name, True), quote=False)
            s = PH.sub(in_text, tok)
            if tx.lang == "bn" and s.strip() and not LETTERS.search(s):
                s = digits_outside_entities(s)
            out.append(s)
    return "".join(out)


# --------------------------------------------------------------------------- Bangla pages: addresses and fonts
def bn_urls(h, base, pages):
    """Inside the /bn/ folder, links to pictures, style sheet etc. need one step up; page links stay."""
    def fix(am):
        url = am.group(2)
        if url.startswith(("http:", "https:", "mailto:", "tel:", "#", "//", "data:", "javascript:")):
            return am.group(0)
        path = re.split(r"[?#]", url, maxsplit=1)[0]
        if path in ("", "./") or path in pages:
            return am.group(0)
        return am.group(1) + "../" + url + am.group(3)
    parts = []
    for tok in TOKEN.split(h):
        if tok.startswith("<") and not tok.startswith("<!--"):
            tok = re.sub(r'(\s(?:href|src)=")([^"]*)(")', fix, tok)
        parts.append(tok)
    return "".join(parts)


def bangla(h, slug, base, pages):
    h = bn_urls(h, base, pages)
    h = h.replace('<html lang="en">', '<html lang="bn">', 1)
    h = re.sub(r'class="ls-en" href="([^"]*)" lang="en" hreflang="en" aria-current="true"',
               lambda m: f'class="ls-en" href="../{"" if m.group(1) in ("./", "../") else m.group(1).replace("../", "")}" lang="en" hreflang="en"', h)
    h = re.sub(r'class="ls-bn" href="[^"]*"', f'class="ls-bn" href="{"./" if slug == "index" else slug}" aria-current="true"', h)
    p = "" if slug == "index" else slug
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{base}/bn/{p}">', h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{base}/bn/{p}"><meta property="og:locale" content="bn_BD">', h)
    return h.replace("&display=swap", BN_FONTS, 1)


# --------------------------------------------------------------------------- main
def main():
    settings = read_settings(os.path.join(CONTENT, "_site.txt"))
    base = settings["site_url"].rstrip("/")
    shared = read_content(os.path.join(CONTENT, "_shared.txt"))
    partials = {n: read(os.path.join(TEMPLATES, f"_{n}.html")) for n in ("head", "header", "footer")}
    svgs = {f[:-4]: read(os.path.join(TEMPLATES, "_svg", f)).strip() for f in os.listdir(os.path.join(TEMPLATES, "_svg")) if f.endswith(".svg")}
    slugs = sorted(f[:-5] for f in os.listdir(TEMPLATES) if f.endswith(".html") and not f.startswith("_"))
    bn_pages = {s for s in slugs if s not in ENGLISH_ONLY}

    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(STATIC, OUT)
    os.makedirs(os.path.join(OUT, "bn"), exist_ok=True)

    fallbacks, used_shared, unused = set(), set(), []
    for slug in slugs:
        page = read_content(os.path.join(CONTENT, slug + ".txt"))
        layout = assemble(slug, partials, svgs)
        used_page = set()
        for lang in ("en", "bn"):
            if lang == "bn" and slug in ENGLISH_ONLY:
                continue
            tx = Texts(page, shared, settings, lang, fallbacks if slug not in ENGLISH_ONLY else set())
            try:
                h = fill(layout, tx)
            except BuildError as e:
                raise BuildError(f"page '{slug}' ({lang}): {e}")
            if "{{" in h or "}}" in h:
                bad = re.search(r".{0,40}(\{\{|\}\}).{0,40}", h).group(0)
                raise BuildError(f"page '{slug}' ({lang}): a {{{{ }}}} marker was not filled in near: {bad!r}")
            if lang == "bn":
                h = bangla(h, slug, base, bn_pages)
            h = re.sub(r"\n[ \t]+\n", "\n\n", h)
            h = re.sub(r"\n{3,}", "\n\n", h).strip() + "\n"
            path = os.path.join(OUT, "bn" if lang == "bn" else "", slug + ".html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(h)
            used_page |= tx.used
        used_shared |= used_page - set(page)
        unused += [f"{slug}: [{k}]" for k in page if k not in used_page]

    unused += [f"_shared: [{k}]" for k in shared if k not in used_shared]
    urls = "".join(f"<url><loc>{base}/{pre}{'' if s == 'index' else s}</loc></url>"
                   for pre in ("", "bn/") for s in slugs if s != "404" and (pre == "" or s in bn_pages))
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")

    print(f"Built {len(slugs)} English pages and {len(bn_pages)} Bangla pages into _site/")
    if fallbacks:
        print(f"Note: {len(fallbacks)} text(s) have no Bangla yet, so English is shown there: " + ", ".join(sorted(fallbacks)[:8]))
    if unused:
        print(f"Note: {len(unused)} text(s) in content files are not used by any template: " + ", ".join(unused[:8]))


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        print("\nBUILD STOPPED: " + str(e), file=sys.stderr)
        sys.exit(1)
