#!/usr/bin/env python3
"""Pembangun situs KRONIK — Markdown -> HTML statis."""
from __future__ import annotations

import html
import json
from difflib import SequenceMatcher
import math
import re
import shutil
import textwrap
import unicodedata
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
DATA = ROOT / "data"
OUT = ROOT / "docs"
SITE_URL = "https://hendri1202.github.io/sejarah/"

PARTS = [
    {
        "key": "bumi",
        "num": "I",
        "title": "Bumi",
        "sub": "13,8 miliar tahun lalu – sekarang",
        "intro": "Sebelum ada peta, ada debu. Bagian ini mengikuti miliaran tahun pertama: "
                 "bagaimana materi, bintang, dan akhirnya sebuah planet kecil di lengan Orion terbentuk, "
                 "lalu bagaimana planet itu menghabiskan empat miliar tahun untuk menjadi layak dihuni.",
    },
    {
        "key": "manusia",
        "num": "II",
        "title": "Manusia",
        "sub": "7 juta – 2.000 tahun lalu",
        "intro": "Sekelompok kera besar di Afrika timur mulai berdiri tegak. Keturunannya menyebar ke Eropa, "
                 "Asia, dan akhirnya ke kepulauan yang sekarang kita sebut Indonesia — jauh sebelum ada kerajaan, "
                 "bahasa tulis, atau bangsa.",
    },
    {
        "key": "kerajaan",
        "num": "III",
        "title": "Kerajaan",
        "sub": "abad ke-4 – 1527",
        "intro": "Seribu tahun pertama Nusantara yang bisa dibaca dari batu: tujuh prasasti di tepi sungai "
                 "Kalimantan timur, candi-candi di dataran Kedu, dan daftar pulau yang mengaku takluk kepada "
                 "Majapahit — daftar yang panjangnya lebih banyak soal ambisi daripada kenyataan.",
    },
    {
        "key": "kolonial",
        "num": "IV",
        "title": "Kolonialisme",
        "sub": "1596 – 1945",
        "intro": "Selama tiga ratus empat puluh tahun, kepulauan ini diatur dari jauh: oleh sebuah perusahaan dagang, "
                 "lalu oleh sebuah kerajaan Eropa. Rempah, kopi, sekolah, dan surat kabar mengubah sebuah wilayah "
                 "menjadi Hindia — dan melahirkan bangsa yang tidak pernah direncanakan. Di antaranya lima perang "
                 "besar yang menguras kas kolonial dan menghabiskan satu generasi.",
    },
    {
        "key": "jepang",
        "num": "V",
        "title": "Perang & Pendudukan",
        "sub": "1929 – 1945",
        "intro": "Depresi, embargo minyak, dan sebuah kekaisaran yang butuh bahan bakar: jalan menuju perang "
                 "di Pasifik ternyata melewati Hindia. Lalu tiga tahun tujuh bulan pendudukan Jepang menghapus "
                 "kekuasaan Belanda dan melatih pemuda Indonesia menjadi tentara — meninggalkan kekosongan "
                 "yang diisi oleh sebuah proklamasi.",
    },
    {
        "key": "merdeka",
        "num": "VI",
        "title": "Kemerdekaan",
        "sub": "1945 – 2026",
        "intro": "Republik ini lahir di teras rumah, diumumkan lewat radio yang sebagian didengar dari mulut ke mulut, "
                 "lalu dipertahankan selama empat tahun dengan senjata bekas dan diplomasi di dua meja. "
                 "Delapan dekade kemudian, pekerjaannya belum selesai.",
    },
]
PART_BY_KEY = {p["key"]: p for p in PARTS}
HAS_FIGURES = False
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]

CAT_LABEL = {
    "bumi": "Bumi",
    "manusia": "Manusia",
    "nusantara": "Nusantara",
    "kolonial": "Kolonial",
    "jepang": "Jepang",
    "merdeka": "Kemerdekaan",
    "modern": "Modern",
}


# ————————————————————————— util —————————————————————————

def esc(s: str) -> str:
    return html.escape(s, quote=True)


def slug_id(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def nf(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def read_frontmatter(raw: str):
    meta: dict = {}
    body = raw
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            block = raw[3:end].strip("\n")
            body = raw[end + 4:].lstrip("\n")
            current_key = None
            for line in block.splitlines():
                if not line.strip():
                    continue
                if line.startswith("  - ") or line.startswith("- "):
                    val = line.strip()[2:].strip()
                    if current_key:
                        meta.setdefault(current_key, []).append(val.strip('"').strip("'"))
                    continue
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    current_key = k
                    if v:
                        meta[k] = v.strip('"').strip("'")
                    else:
                        meta[k] = []
    return meta, body


def load_chapters():
    chapters = []
    for path in sorted(CONTENT.glob("*.md")):
        meta, body = read_frontmatter(path.read_text(encoding="utf-8"))
        if not meta.get("slug"):
            continue
        num = int(meta.get("number", 0))
        dates = []
        for item in meta.get("dates", []) or []:
            if "|" in item:
                when, what = item.split("|", 1)
                dates.append((when.strip(), what.strip()))
        chapters.append({
            "num": num,
            "slug": meta["slug"],
            "part": meta.get("part", "bumi").strip(),
            "title": meta.get("title", "Tanpa judul"),
            "dek": meta.get("dek", ""),
            "span": meta.get("span", ""),
            "dates": dates,
            "sources": [s for s in (meta.get("sources", []) or []) if s],
            "body": body,
            "file": f"{num:02d}-{meta['slug']}.html",
            "words": len(re.findall(r"\w+", body)),
        })
    chapters.sort(key=lambda c: c["num"])
    return chapters


def md_to_html(text: str) -> str:
    notes = []

    def stash(m):
        kind = m.group(1)
        notes.append((kind, m.group(2).strip()))
        return f"\n\nNOTEHOLDER{len(notes) - 1}ENDNOTE\n\n"

    text = re.sub(r":::(note|linimasa)\s*\n(.*?)\n:::", stash, text, flags=re.S)
    text = re.sub(r"^:::.*?:::\s*$", "", text, flags=re.M | re.S)
    converter = markdown.Markdown(extensions=["extra", "toc", "sane_lists", "smarty"],
                                  extension_configs={"toc": {"permalink": False, "toc_depth": "2-2"}})
    out = converter.convert(text)
    md_to_html.last_toc = converter.toc_tokens

    note_no = 0
    for i, (kind, body) in enumerate(notes):
        if kind == "linimasa":
            rows = []
            for line in body.splitlines():
                line = line.strip().lstrip("-").strip()
                if not line:
                    continue
                if "|" in line:
                    when, what = line.split("|", 1)
                else:
                    when, what = "", line
                rows.append(
                    '<li><span class="lm-when">' + esc(when.strip()) + "</span>"
                    '<span class="lm-what">' + esc(what.strip()) + "</span></li>"
                )
            if not rows:
                continue
            block = (
                '\n<div class="linimasa"><span class="micro">Linimasa</span>'
                "<ol>" + "".join(rows) + "</ol></div>\n"
            )
            out = out.replace(f"<p>NOTEHOLDER{i}ENDNOTE</p>", block)
            continue
        note_no += 1
        inner = markdown.markdown(body, extensions=["extra", "smarty"])
        inner = re.sub(r"^<p>(.*?)</p>$", r"\1", inner, flags=re.S)
        block = (
            '\n<aside class="aside"><span class="aside__n">Catatan '
            + str(note_no) + "</span>" + inner + "</aside>\n"
        )
        out = out.replace(f"<p>NOTEHOLDER{i}ENDNOTE</p>", block)

    def pull(m):
        inner = m.group(1).strip()
        return f'<figure class="pullquote"><blockquote>{inner}</blockquote></figure>'

    out = re.sub(r"<blockquote>(.*?)</blockquote>", pull, out, flags=re.S)
    return out


def word_range(n: int) -> str:
    return f"{n:,}".replace(",", ".")


# ————————————————————————— SVG garis waktu —————————————————————————

def sx_log(years_ago: float, x0: float, x1: float, top: float = 13.8e9, cut: float = 12_000) -> float:
    full = math.log10(1 + top)
    start = math.log10(1 + top)
    end = math.log10(1 + cut)
    p = (full - math.log10(1 + years_ago)) / (start - end)
    return x0 + max(0.0, min(1.0, p)) * (x1 - x0)


def sx_lin(years_ago: float, x0: float, x1: float, left_ago: float, right_ago: float) -> float:
    p = (left_ago - years_ago) / (left_ago - right_ago)
    return x0 + max(0.0, min(1.0, p)) * (x1 - x0)


def _tw(s: str, px: float) -> float:
    """Perkiraan lebar teks (cukup untuk menghindari tabrakan label)."""
    narrow = sum(1 for ch in s if ch in "iljfrts.,:;'’ ")
    wide = sum(1 for ch in s if ch in "mwMW")
    other = len(s) - narrow - wide
    return (narrow * 0.34 + wide * 0.86 + other * 0.55) * px


def rail(segments, markers, width=1200):
    """segments: [(label, x_a, x_b, key)]; markers: [(x, tanggal, peristiwa, href)]"""
    h = 172
    axis = 112
    rows = [axis - 16, axis - 40, axis - 64]
    out = ['<svg viewBox="0 0 %d %d" role="img" aria-label="Garis waktu" xmlns="http://www.w3.org/2000/svg">' % (width, h)]

    # pita bagian
    era_rows = [[], []]
    for label, xa, xb, key in segments:
        w = max(3.0, xb - xa)
        fill = "var(--accent)" if key == "jepang" else "var(--paper-3)"
        out.append(
            f'<rect x="{xa:.1f}" y="{axis + 2}" width="{w:.1f}" height="8" fill="{fill}"/>'
        )
        cx = xa + w / 2
        tw = _tw(label.upper(), 10.5) + len(label) * 1.7
        if w < tw + 8:
            # pita terlalu sempit: rapatkan label ke kanan, beri penunjuk
            out.append(f'<line x1="{cx:.1f}" y1="{axis + 10}" x2="{cx:.1f}" y2="{axis + 16}" stroke="var(--accent)" stroke-width="1"/>')
        placed = False
        for ri, row in enumerate(era_rows):
            lo, hi = cx - tw / 2, cx + tw / 2
            if all(hi < a - 10 or lo > b + 10 for a, b in row):
                row.append((lo, hi))
                out.append(
                    f'<text x="{cx:.1f}" y="{axis + 26 + ri * 15}" class="rail-era{" rail-era--tight" if key == "jepang" else ""}" text-anchor="middle">{esc(label.upper())}</text>'
                )
                placed = True
                break
        if not placed:
            out.append(f'<text x="{cx:.1f}" y="{axis + 26}" class="rail-era" text-anchor="middle">{esc(label.upper())}</text>')

    # garis dasar
    out.append(f'<line x1="0" y1="{axis}" x2="{width}" y2="{axis}" stroke="var(--rule)" stroke-width="1"/>')

    # penanda + label tiga baris
    occ = [[], [], []]
    for i, m in enumerate(markers):
        x, dt, ev = m[0], m[1], m[2]
        href = m[3] if len(m) > 3 else ""
        w = _tw(dt, 13) + 6 + _tw(ev, 10.5)
        if x - w / 2 < 4:
            anchor, tx, lo, hi = "start", x + 7, x + 7, x + 7 + w
        elif x + w / 2 > width - 4:
            anchor, tx, lo, hi = "end", x - 7, x - 7 - w, x - 7
        else:
            anchor, tx, lo, hi = "middle", x, x - w / 2, x + w / 2
        best, best_cost = 0, 1e9
        for ri, row in enumerate(occ):
            cost = sum(max(0.0, min(hi, b) - max(lo, a) + 12) for a, b in row)
            if cost == 0:
                best = ri
                break
            if cost < best_cost:
                best, best_cost = ri, cost
        occ[best].append((lo, hi))
        ry = rows[best]
        g_open = f'<a href="{href}">' if href else "<g>"
        g_close = "</a>" if href else "</g>"
        out.append(g_open)
        out.append(f'<line x1="{x:.1f}" y1="{axis - 4}" x2="{x:.1f}" y2="{ry + 5}" stroke="var(--rule)" stroke-width="1"/>')
        if abs(tx - x) > 3:
            out.append(f'<line x1="{x:.1f}" y1="{ry + 5}" x2="{tx:.1f}" y2="{ry + 5}" stroke="var(--rule)" stroke-width="1"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{axis - 5}" r="2.8" fill="var(--paper)" stroke="var(--ink)" stroke-width="1.1"/>')
        out.append(
            f'<text x="{tx:.1f}" y="{ry}" text-anchor="{anchor}">'
            f'<tspan class="rail-t">{esc(dt)}</tspan>'
            f'<tspan class="rail-s" dx="5">{esc(ev)}</tspan></text>'
        )
        out.append(g_close)
    out.append("</svg>")
    return "".join(out)


def _rail_links(chapters):
    by = {c["num"]: c["file"] for c in chapters}
    return by


def deep_rail(files):
    X = lambda y: sx_log(y, 0, 1200)
    segs = [("Bumi", X(13.8e9), X(66e6), "bumi"), ("Manusia", X(66e6), 1198, "manusia")]
    marks = [
        (X(13.8e9), "13,8 miliar", "Dentuman Besar", files.get(1, "")),
        (X(4.54e9), "4,54 miliar", "Bumi terbentuk", files.get(2, "")),
        (X(2.4e9), "2,4 miliar", "Oksigen di udara", files.get(3, "")),
        (X(541e6), "541 juta", "Ledakan Kambrium", files.get(4, "")),
        (X(252e6), "252 juta", "Kepunahan Perm-Trias", files.get(4, "")),
        (X(66e6), "66 juta", "Dinosaurus habis", files.get(5, "")),
        (X(7e6), "7 juta", "Hominin pertama", files.get(7, "")),
        (X(300_000), "300 ribu", "Homo sapiens", files.get(10, "")),
        (X(12_000), "12 ribu", "Akhir zaman es", files.get(11, "")),
    ]
    return rail(segs, marks)


def era_rail(left_ago, right_ago, segments, markers):
    x_of = lambda y: sx_lin(y, 0, 1200, left_ago, right_ago)
    segs = [(lbl, x_of(a), x_of(b), key) for lbl, a, b, key in segments]
    marks = [(x_of(y), t, s, href) for y, t, s, href in markers]
    return rail(segs, marks)


# ————————————————————————— kerangka —————————————————————————

FONTS = '<link rel="stylesheet" href="assets/fonts.css">'

FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
    "%3Crect width='64' height='64' fill='%23f2ebdb'/%3E"
    "%3Ctext x='32' y='47' font-family='Georgia,serif' font-size='44' text-anchor='middle' fill='%231a1610'%3EK%3C/text%3E"
    "%3C/svg%3E"
)

EARLY_THEME = (
    "<script>try{var t=localStorage.getItem('kronik-theme');"
    "if(!t&&matchMedia('(prefers-color-scheme: dark)').matches)t='malam';"
    "if(t)document.documentElement.setAttribute('data-theme',t);"
    "if(location.search.indexOf('tema=malam')>-1)document.documentElement.setAttribute('data-theme','malam')"
    "}catch(e){}</script>"
)


def masthead(current=""):
    return f"""
<header class="masthead">
  <div class="masthead__inner">
    <a class="brand" href="index.html">Kronik<span>Sejarah</span></a>
    <span class="micro brand-sub">Nusantara &amp; dunia</span>
    <div class="masthead__spacer"></div>
    <div class="tools">
      <button class="tool" type="button" data-drawer-open aria-controls="daftar-isi">Isi</button>
      <button class="tool" type="button" data-search-open>Cari <kbd>/</kbd></button>
      <button class="tool" type="button" data-theme-toggle aria-pressed="false">Malam</button>
    </div>
  </div>
  <span class="progress" aria-hidden="true"></span>
</header>"""


def drawer(chapters):
    fig_drawer = ('<li><a href="tokoh.html"><span class="n">→</span><span>Tokoh</span></a></li>'
                  if HAS_FIGURES else "")
    blocks = []
    for part in PARTS:
        items = [c for c in chapters if c["part"] == part["key"]]
        if not items:
            continue
        lis = "".join(
            f'<li><a href="{c["file"]}"><span class="n">{c["num"]:02d}</span><span>{esc(c["title"])}</span></a></li>'
            for c in items
        )
        blocks.append(
            f'<div class="drawer__part"><span class="micro">{part["num"]} · {esc(part["title"])}</span>'
            f"<ol>{lis}</ol></div>"
        )
    return f"""
<aside class="drawer" id="daftar-isi" data-open="false" aria-hidden="true" aria-label="Daftar isi">
  <div class="drawer__head">
    <h2>Daftar isi</h2>
    <button class="tool" type="button" data-drawer-close>Tutup</button>
  </div>
  {"".join(blocks)}
  <div class="drawer__part"><span class="micro">Rujukan</span><ol>
    <li><a href="kronologi.html"><span class="n">→</span><span>Kronologi lengkap</span></a></li>
    {fig_drawer}
    <li><a href="glosarium.html"><span class="n">→</span><span>Glosarium</span></a></li>
    <li><a href="tentang.html"><span class="n">→</span><span>Tentang &amp; sumber</span></a></li>
  </ol></div>
</aside>
<div class="scrim" data-open="false"></div>"""


def search_panel():
    return """
<div class="search" role="dialog" aria-modal="true" aria-label="Cari di Kronik">
  <div class="search__panel">
    <div class="search__box">
      <input type="search" placeholder="Cari bab, peristiwa, atau istilah…" aria-label="Kata kunci" autocomplete="off">
      <button class="tool" type="button" data-search-close>Tutup</button>
    </div>
    <ul class="search__results"></ul>
  </div>
</div>"""


def footer():
    fig_link = '<a class="micro" href="tokoh.html">Tokoh</a>' if HAS_FIGURES else ""
    return f"""
<footer class="foot">
  <div class="wrap foot__inner">
    <a class="foot__mark" href="index.html">Kronik</a>
    <span class="micro">26 bab · 6 bagian · Edisi {BULAN[date.today().month - 1]} {date.today().year}</span>
    <nav>
      <a class="micro" href="kronologi.html">Kronologi</a>
      {fig_link}
      <a class="micro" href="glosarium.html">Glosarium</a>
      <a class="micro" href="tentang.html">Tentang</a>
    </nav>
  </div>
</footer>"""


def page(title, desc, body, url="", cls=""):
    full_title = title if title.startswith("Kronik") else f"{title} — Kronik"
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#f2ebdb">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:site_name" content="Kronik">
<meta property="og:image" content="{SITE_URL}assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{f'<link rel="canonical" href="{SITE_URL}{url}">' if url else ''}
<link rel="icon" href="{FAVICON}">
{FONTS}
<link rel="stylesheet" href="assets/style.css">
{EARLY_THEME}
</head>
<body class="{cls}">
<a class="skip" href="#isi">Lompat ke isi</a>
{body}
<script src="assets/index-data.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
"""


# ————————————————————————— halaman —————————————————————————

def build_index(chapters):
    part_blocks = []
    for part in PARTS:
        items = [c for c in chapters if c["part"] == part["key"]]
        if not items:
            continue
        rows = "".join(
            f'<li><a href="{c["file"]}"><span class="n">{c["num"]:02d}</span>'
            f'<span class="t">{esc(c["title"])}</span><span class="lead"></span>'
            f'<span class="d">{esc(c["span"])}</span></a></li>'
            for c in items
        )
        part_blocks.append(f"""
<section class="part" id="{part["key"]}">
  <div class="part__num" aria-hidden="true">{part["num"]}</div>
  <div>
    <h2 class="part__title">{esc(part["title"])}</h2>
    <div class="part__meta"><span class="micro">{len(items)} bab</span><span class="micro" style="opacity:.5">·</span><span class="micro">{esc(part["sub"])}</span></div>
    <p class="part__intro">{esc(part["intro"])}</p>
    <ol class="chapters">{rows}</ol>
  </div>
</section>""")

    files = _rail_links(chapters)
    deep = deep_rail(files)
    middle = era_rail(
        12_000, 426,
        [("Manusia", 12_000, 1_700, "manusia"), ("Kerajaan", 1_700, 426, "kerajaan")],
        [
            (10_000, "10.000 tahun lalu", "Pertanian pertama", files.get(11, "")),
            (3_500, "3.500 tahun lalu", "Pelaut Austronesia", files.get(11, "")),
            (1_700, "abad ke-4", "Prasasti Kutai", files.get(12, "")),
            (1_100, "abad ke-9", "Sriwijaya", files.get(12, "")),
            (700, "abad ke-14", "Majapahit", files.get(13, "")),
            (426, "1602", "VOC berdiri", files.get(14, "")),
        ],
    )
    late = era_rail(
        426, 0,
        [("Kolonial", 426, 84, "kolonial"), ("Jepang", 84, 81, "jepang"), ("Merdeka", 81, 0, "merdeka")],
        [
            (426, "1596", "Armada Houtman", files.get(14, "")),
            (196, "1830", "Tanam paksa", files.get(15, "")),
            (118, "1908", "Boedi Oetomo", files.get(17, "")),
            (84, "1942", "Jepang mendarat", files.get(20, "")),
            (81, "1945", "Proklamasi", files.get(22, "")),
            (61, "1965", "G30S", files.get(24, "")),
            (28, "1998", "Reformasi", files.get(25, "")),
            (0, "2026", "Sekarang", files.get(26, "")),
        ],
    )

    total_words = sum(c["words"] for c in chapters)

    body = f"""{masthead()}
{drawer(chapters)}
<main id="isi">
<section class="hero wrap">
  <div class="hero__top">
    <span class="micro micro--ink">Arsip sejarah · Edisi 01</span>
    <span class="micro micro--ink">{len(chapters)} bab · 6 bagian · ± {word_range(total_words)} kata</span>
  </div>
  <h1>Dari debu bintang<em>sampai proklamasi.</em></h1>
  <div class="hero__lede">
    <p>Bumi ini berumur 4,54 miliar tahun. Manusia baru muncul di detik-detik terakhirnya. Republik ini
    bahkan lebih muda lagi: delapan dekade, sekitar satu per lima puluh juta dari seluruh riwayat planet.
    Kronik menyusun rentang raksasa itu menjadi {len(chapters)} bab yang bisa dibaca berurutan — dari ledakan yang
    memulai segalanya, sampai pemilu yang baru saja lewat.</p>
    <p>Setiap bab berdiri sendiri, tetapi benangnya satu: bagaimana sebuah kepulauan di antara dua samudra
    menjadi tempat bertemunya pelaut, pedagang, penjajah, dan akhirnya sebuah bangsa.</p>
  </div>
  <p class="note">Tanggal dan angka di situs ini mengikuti literatur geologi, arkeologi, dan sejarah
  Indonesia yang lazim dipakai. Kalau suatu perkiraan masih diperdebatkan, perdebatannya ikut ditulis.
  <a href="tentang.html">Baca catatan metode →</a></p>

  <div class="railband">
    <div class="railband__head">
      <span class="micro">Skala waktu · panel 1 dari 3</span>
      <span class="rail-cap">logaritma, 13,8 miliar tahun</span>
    </div>
    <div class="rail-scroll">{deep}</div>
    <span class="rail-hint">geser →</span>
    <div class="railband__head" style="margin-top:22px">
      <span class="micro">Panel 2 · 12.000 tahun terakhir</span>
      <span class="rail-cap">linear</span>
    </div>
    <div class="rail-scroll">{middle}</div>
    <div class="railband__head" style="margin-top:22px">
      <span class="micro">Panel 3 · empat abad terakhir</span>
      <span class="rail-cap">linear, diperbesar</span>
    </div>
    <div class="rail-scroll">{late}</div>
    <p class="rail-cap" style="margin:14px 0 0">Pada panel terakhir, tiga tahun pendudukan Jepang selebar
    kurang dari satu persen. Skala tidak pernah netral.</p>
  </div>
</section>

<section class="wrap pad" id="daftar">
  <div class="toc-head">
    <h2>Isi</h2>
    <span class="micro">Dibaca berurutan, atau tidak sama sekali</span>
  </div>
  {"".join(part_blocks)}
</section>

<section class="wrap" style="padding-bottom:clamp(40px,7vw,90px)">
  <div class="toc-head" style="border:0;padding:0;margin:0">
    <p style="max-width:52ch;color:var(--ink-2);margin:0">Butuh satu halaman untuk melihat semuanya sekaligus?
    Kronologi menyusun {len(chapters)} bab itu menjadi satu garis waktu, dan glosarium menjelaskan istilah yang
    dilewati tanpa penjelasan.</p>
  </div>
  <p style="display:flex;gap:22px;flex-wrap:wrap;margin-top:18px">
    <a class="micro" style="border-bottom:1px solid var(--rule);padding-bottom:3px" href="kronologi.html">Buka kronologi →</a>
    <a class="micro" style="border-bottom:1px solid var(--rule);padding-bottom:3px" href="glosarium.html">Buka glosarium →</a>
  </p>
</section>
</main>
{footer()}
{search_panel()}"""

    return page("Kronik — Sejarah panjang bumi, manusia, dan Indonesia",
                "Sejarah lengkap dalam 26 bab: pembentukan bumi, manusia purba, kerajaan Nusantara, penjajahan Belanda, pendudukan Jepang, dan kemerdekaan Indonesia.",
                body, url="", cls="page-home")


def build_chapter(ch, chapters):
    part = PART_BY_KEY[ch["part"]]
    idx = chapters.index(ch)
    prev_ch = chapters[idx - 1] if idx > 0 else None
    next_ch = chapters[idx + 1] if idx + 1 < len(chapters) else None
    minutes = max(3, round(ch["words"] / 210))

    dates_html = "".join(
        f'<span><b>{esc(when)}</b> {esc(what)}</span>' for when, what in ch["dates"]
    )
    sources_html = "".join(f"<li>{esc(s)}</li>" for s in ch["sources"]) or "<li>—</li>"

    next_html = ""
    if next_ch:
        next_html = (
            f'<a href="{next_ch["file"]}"><span class="micro">Bab {next_ch["num"]:02d} · {esc(PART_BY_KEY[next_ch["part"]]["title"])}</span>'
            f'<span class="t">{esc(next_ch["title"])}</span></a>'
        )
    if prev_ch:
        next_html += (
            f'<a href="{prev_ch["file"]}" style="margin-top:10px"><span class="micro">Sebelumnya · Bab {prev_ch["num"]:02d}</span>'
            f'<span class="t">{esc(prev_ch["title"])}</span></a>'
        )
    next_html += '<a href="index.html#daftar" style="margin-top:10px"><span class="micro">Daftar isi</span><span class="t">Semua bab</span></a>'

    body_html = md_to_html(ch["body"])
    toc_items = "".join(
        f'<li><a href="#{t["id"]}">{esc(t["name"])}</a></li>'
        for t in (md_to_html.last_toc or []) if t.get("level") == 2
    )
    toc_html = (
        f'<nav class="chapter-toc" aria-label="Isi bab"><span class="micro">Dalam bab ini</span>'
        f'<ol>{toc_items}</ol></nav>'
    ) if toc_items else ""

    body = f"""{masthead(ch["slug"])}
{drawer(chapters)}
<main id="isi">
<article class="chapter wrap" data-prev="{prev_ch["file"] if prev_ch else ""}" data-next="{next_ch["file"] if next_ch else ""}">
  <header class="chapter__head">
    <div class="chapter__ghost" aria-hidden="true">{ch["num"]:02d}</div>
    <div class="chapter__kicker">
      <a class="micro" href="index.html#{ch["part"]}">Bagian {part["num"]} · {esc(part["title"])}</a>
      <span class="micro">Bab {ch["num"]:02d} / {len(chapters)}</span>
    </div>
    <h1>{esc(ch["title"])}</h1>
    <p class="chapter__dek">{esc(ch["dek"])}</p>
    <div class="chapter__meta">
      <span class="micro">Rentang <b style="color:var(--ink)">{esc(ch["span"])}</b></span>
      <div class="dates">{dates_html}</div>
      <span class="micro" style="margin-left:auto">{word_range(ch["words"])} kata · ± {minutes} menit</span>
    </div>
  </header>

  {toc_html}

  <div class="layout">
    <div class="prose">{body_html}</div>
  </div>

  <footer class="chapter__end">
    <section class="sources">
      <h3 class="micro">Bacaan</h3>
      <ol>{sources_html}</ol>
    </section>
    <section class="next">
      <h3 class="micro">Lanjut</h3>
      {next_html}
    </section>
  </footer>
</article>
</main>
{footer()}
{search_panel()}"""

    return page(ch["title"],
                ch["dek"] or f"Bab {ch['num']} Kronik: {ch['title']}",
                body, url=ch["file"], cls="page-chapter")


def build_timeline(chapters):
    raw = json.loads((DATA / "timeline.json").read_text(encoding="utf-8"))
    raw.sort(key=lambda e: (e["year"], e.get("when", "")))
    counts = {}
    for e in raw:
        counts[e["cat"]] = counts.get(e["cat"], 0) + 1

    chips = ['<button class="chip" type="button" data-filter="semua" aria-pressed="true">Semua<span class="c">'
             + str(len(raw)) + "</span></button>"]
    for key in ["bumi", "manusia", "nusantara", "kolonial", "jepang", "merdeka", "modern"]:
        if key not in counts:
            continue
        chips.append(
            f'<button class="chip" type="button" data-filter="{key}" aria-pressed="false">'
            f'{CAT_LABEL[key]}<span class="c">{counts[key]}</span></button>'
        )

    rows = []
    for i, e in enumerate(raw):
        cat = e["cat"]
        label = CAT_LABEL.get(cat, cat.title())
        anchor = f'y{e["year"]}-{i}'
        rows.append(f"""
<li class="tl" data-cat="{cat}" id="{anchor}">
  <span class="tl__when">{esc(e.get("when", str(e["year"])))}</span>
  <span class="tl__dot" aria-hidden="true"><i></i></span>
  <div class="tl__body">
    <p class="tl__title">{esc(e["title"])}<span class="tl__cat">{label}</span></p>
    <p class="tl__blurb">{esc(e.get("blurb", ""))}</p>
  </div>
</li>""")

    body = f"""{masthead()}
{drawer(chapters)}
<main id="isi">
<section class="wrap">
  <header class="page-head">
    <div class="chapter__kicker">
      <span class="micro">Rujukan · Kronologi</span>
      <span class="micro" data-tl-count>{len(raw)} peristiwa</span>
    </div>
    <h1>Kronologi</h1>
    <p>{len(raw)} titik dari 13,8 miliar tahun, disusun berurutan. Saring menurut bagian, atau telusuri
    dari atas ke bawah seperti membaca strata batuan.</p>
  </header>
</section>
<div class="wrap"><div class="filters">{"".join(chips)}</div></div>
<section class="wrap" style="padding-bottom:clamp(40px,7vw,80px)">
  <ol class="timeline">{"".join(rows)}</ol>
</section>
</main>
{footer()}
{search_panel()}"""
    return page("Kronologi", "Garis waktu lengkap dari Dentuman Besar sampai Indonesia hari ini.",
                body, url="kronologi.html", cls="page-timeline")


def build_glossary(chapters):
    raw = json.loads((DATA / "glossary.json").read_text(encoding="utf-8"))
    raw.sort(key=lambda g: g["term"].lower())

    groups = []
    for g in raw:
        letter = g["term"][0].upper()
        if not groups or groups[-1][0] != letter:
            groups.append((letter, []))
        groups[-1][1].append(g)

    sections = []
    for letter, items in groups:
        entries = "".join(
            f'<div class="gterm" id="{slug_id(g["term"])}"><h3>{esc(g["term"])}</h3><p>{esc(g["def"])}</p></div>'
            for g in items
        )
        sections.append(
            f'<section class="gletter"><h2 class="gletter__l">{letter}</h2>'
            f'<div class="glist">{entries}</div></section>'
        )

    body = f"""{masthead()}
{drawer(chapters)}
<main id="isi">
<section class="wrap">
  <header class="page-head">
    <div class="chapter__kicker"><span class="micro">Rujukan · Glosarium</span><span class="micro">{len(raw)} istilah</span></div>
    <h1>Glosarium</h1>
    <p>Istilah yang muncul di sepanjang Kronik tanpa selalu dijelaskan: dari nama zaman geologi sampai
    singkatan politik tahun 1945.</p>
  </header>
  {"".join(sections)}
</section>
</main>
{footer()}
{search_panel()}"""
    return page("Glosarium", "Istilah geologi, arkeologi, kolonial, dan politik Indonesia.",
                body, url="glosarium.html", cls="page-glossary")


def norm_years(life: str) -> str:
    life = re.sub(r"(\d)\s*-\s*(\d)", "\1–\2", life)
    life = re.sub(r"(\d)-$", "\1–", life)
    return life


def build_figures(figures, chapters):
    by_num = {c["num"]: c for c in chapters}
    groups = []
    for f in figures:
        letter = f["name"][0].upper()
        if not groups or groups[-1][0] != letter:
            groups.append((letter, []))
        groups[-1][1].append(f)

    sections = []
    for letter, items in groups:
        rows = []
        for f in items:
            ch = by_num.get(int(f.get("chapter", 0)))
            link = (f'<a class="tfig__ch" href="{ch["file"]}">Bab {ch["num"]:02d}</a>'
                    if ch else "")
            rows.append(
                f'<li class="tfig" id="{slug_id(f["name"])}">'
                f'<span class="tfig__who"><span class="tfig__name">{esc(f["name"])}</span>'
                f'<span class="tfig__life">{esc(f.get("life", ""))}</span></span>'
                f'<span class="tfig__role">{esc(f.get("role", ""))}</span>'
                f"{link}</li>"
            )
        sections.append(
            f'<section class="gletter"><h2 class="gletter__l">{letter}</h2>'
            f'<ul class="tfigs">{"".join(rows)}</ul></section>'
        )

    body = f"""{masthead()}
{drawer(chapters)}
<main id="isi">
<section class="wrap">
  <header class="page-head">
    <div class="chapter__kicker"><span class="micro">Rujukan · Tokoh</span><span class="micro">{len(figures)} nama</span></div>
    <h1>Tokoh</h1>
    <p>Orang-orang yang menggerakkan bab-bab di situs ini: dari astronom yang mengukur alam semesta
    sampai pemuda yang mengetik teks proklamasi. Tiap nama menunjuk ke bab tempat ia muncul.</p>
  </header>
  {"".join(sections)}
</section>
</main>
{footer()}
{search_panel()}"""
    return page("Tokoh", "Indeks tokoh sejarah dalam Kronik, dari kosmologi sampai Indonesia modern.",
                body, url="tokoh.html", cls="page-figures")


def build_about(chapters):
    raw_sources = sorted({s for c in chapters for s in c["sources"]})
    sources = []
    for cand in raw_sources:
        if not any(SequenceMatcher(None, cand, kept).ratio() > 0.82 for kept in sources):
            sources.append(cand)
    src_html = "".join(f"<li>{esc(s)}</li>" for s in sources)
    words = sum(c["words"] for c in chapters)

    body = f"""{masthead()}
{drawer(chapters)}
<main id="isi">
<section class="wrap">
  <header class="page-head">
    <div class="chapter__kicker"><span class="micro">Rujukan · Tentang</span><span class="micro">Edisi 01</span></div>
    <h1>Tentang Kronik</h1>
    <p>Situs ini mencoba melakukan sesuatu yang sederhana dan sulit: menaruh seluruh riwayat bumi, manusia,
    dan Indonesia dalam satu tarikan napas — tanpa memotong sudut yang penting.</p>
  </header>
  <div class="about-grid">
    <div class="prose notes">
      <h2>Cara membaca</h2>
      <p>{len(chapters)} bab tersusun kronologis, masing-masing sekitar tiga ribu sampai empat ribu kata, dan
      ditulis supaya bisa dibaca sendirian. Setiap bab punya daftar isi sendiri di atas, penanda waktu di kepala,
      catatan di tepi halaman, dan linimasa ringkas di ujungnya. Kalau kamu baru datang, mulai dari daftar isi
      dan ikuti nomornya. Kalau kamu sedang mencari satu peristiwa, kronologi punya
      {len(json.loads((DATA / 'timeline.json').read_text(encoding='utf-8')))} titik yang bisa disaring.
      Tombol <em>Cari</em> atau garis miring di kibor membuka pencarian cepat.</p>
      <p>Catatan di tepi halaman — yang bergaris atas tipis — bukan hiasan: isinya angka pembanding, koreksi,
      atau versi lain dari cerita yang sedang dibaca.</p>

      <h2>Soal akurasi</h2>
      <p>Sejarah punya dua jenis ketidakpastian. Yang pertama teknis: umur batuan, ukuran populasi, jumlah
      korban. Untuk hal seperti ini, situs ini memakai rentang dan menyebut bahwa itu perkiraan. Yang kedua
      politis: siapa yang dianggap pahlawan, kapan sebuah perang dimulai, apakah suatu peristiwa disebut
      pemberontakan atau perlawanan. Untuk hal seperti ini, situs ini berusaha menuliskan perdebatan itu
      sebagai perdebatan, bukan memilih satu versi lalu menyembunyikan yang lain.</p>
      <p>Kutipan langsung hanya dipakai bila redaksinya memang terdokumentasi, seperti teks proklamasi.
      Selebihnya parafrasa.</p>

      <h2>Batas</h2>
      <p>Tidak ada gambar di situs ini. Bukan karena sejarah tidak butuh gambar, tetapi karena gambar sejarah
      hampir selalu punya pemilik, dan yang tidak punya pemilik sering salah keterangan. Yang dipakai sebagai
      pengganti adalah skala: garis waktu, angka, dan urutan. Kalau nanti ada versi bergambar, gambar akan
      diberi keterangan sumber lengkap.</p>
      <p>Situs ini juga tidak mengklaim sebagai sumber primer. Ia adalah pintu masuk. Daftar bacaan di akhir
      setiap bab adalah tempat yang seharusnya dituju.</p>

      <h2>Kolofon</h2>
      <p>Seluruh {word_range(words)} kata disusun dalam {len(chapters)} bab dan {len(PARTS)} bagian. Huruf judul
      Instrument Serif, teks Source Serif 4, label dan angka JetBrains Mono. Warna diambil dari kertas tua dan
      tinta oksida besi — bukan dari gradien. Situs statis, tanpa pelacak, tanpa iklan.</p>
      <p>Dibangun dan diperbarui {date.today().year}.</p>

      <h2>Bacaan</h2>
      <ol class="sources-list">{src_html}</ol>
    </div>
    <aside class="about-side">
      <span class="micro">Ringkasan</span>
      <dl>
        <div><dt>Bagian</dt><dd>{len(PARTS)}</dd></div>
        <div><dt>Bab</dt><dd>{len(chapters)}</dd></div>
        <div><dt>Kata</dt><dd>{word_range(words)}</dd></div>
        <div><dt>Peristiwa di kronologi</dt><dd>{len(json.loads((DATA / 'timeline.json').read_text(encoding='utf-8')))}</dd></div>
        <div><dt>Istilah di glosarium</dt><dd>{len(json.loads((DATA / 'glossary.json').read_text(encoding='utf-8')))}</dd></div>
        <div><dt>Rujukan</dt><dd>{len(sources)}</dd></div>
      </dl>
      <p class="micro" style="margin-top:18px;line-height:1.7">Edisi {date.today().year} · tanpa pelacak</p>
    </aside>
  </div>

  <div class="colophon">
    <div><b>Isi</b>{len(chapters)} bab · {len(PARTS)} bagian · {word_range(words)} kata</div>
    <div><b>Huruf</b>Instrument Serif · Source Serif 4 · JetBrains Mono</div>
    <div><b>Palet</b>Kertas #f2ebdb · Tinta #1a1610 · Oksida #9c3a1f</div>
    <div><b>Format</b>{len(chapters)} bab · ± 3.400 kata per bab</div>
    <div><b>Teknis</b>HTML statis, tanpa pelacak</div>
  </div>
</section>
</main>
{footer()}
{search_panel()}"""
    return page("Tentang", "Cara Kronik disusun, batasannya, dan daftar bacaan.", body,
                url="tentang.html", cls="page-about")


def build_404(chapters):
    body = f"""{masthead()}
{drawer(chapters)}
<main id="isi">
<section class="wrap pad">
  <div class="page-head">
    <span class="micro">Galat 404</span>
    <h1>Halaman ini<br>tidak tercatat.</h1>
    <p>Mungkin tautannya salah, mungkin babnya belum ditulis. Daftar isi selalu punya jawaban.</p>
    <p style="margin-top:22px"><a class="micro" style="border-bottom:1px solid var(--rule);padding-bottom:3px" href="index.html">Kembali ke daftar isi →</a></p>
  </div>
</section>
</main>
{footer()}
{search_panel()}"""
    return page("Tidak ditemukan", "Halaman tidak ditemukan.", body, cls="page-404")


def build_search_index(chapters):
    entries = []
    for c in chapters:
        part = PART_BY_KEY[c["part"]]
        plain = re.sub(r":::note", " ", c["body"])
        plain = re.sub(r"[#>*_`|]", " ", plain)
        plain = re.sub(r"\s+", " ", plain).strip()[:6000]
        entries.append({
            "t": c["title"],
            "k": f"Bab {c['num']:02d} · {part['title']}",
            "u": c["file"],
            "d": c["span"],
            "x": c["dek"] + " " + plain,
        })
    try:
        tl = json.loads((DATA / "timeline.json").read_text(encoding="utf-8"))
        tl.sort(key=lambda e: e["year"])
        for i, e in enumerate(tl):
            entries.append({
                "t": e["title"],
                "k": "Kronologi · " + CAT_LABEL.get(e["cat"], e["cat"]).title(),
                "u": f'kronologi.html#y{e["year"]}-{i}',
                "d": e.get("when", ""),
                "x": e.get("blurb", ""),
            })
    except Exception as exc:  # noqa: BLE001
        print("  ! timeline dilewati:", exc)
    try:
        gl = json.loads((DATA / "glossary.json").read_text(encoding="utf-8"))
        for g in gl:
            entries.append({
                "t": g["term"],
                "k": "Glosarium",
                "u": "glosarium.html#" + slug_id(g["term"]),
                "d": "",
                "x": g["def"],
            })
    except Exception as exc:  # noqa: BLE001
        print("  ! glosarium dilewati:", exc)
    if HAS_FIGURES:
        try:
            figs = json.loads((DATA / "figures.json").read_text(encoding="utf-8"))
            by_num = {c["num"]: c for c in chapters}
            for f in figs:
                ch = by_num.get(int(f.get("chapter", 0)))
                entries.append({
                    "t": f["name"],
                    "k": "Tokoh" + (f" · Bab {ch['num']:02d}" if ch else ""),
                    "u": "tokoh.html#" + slug_id(f["name"]),
                    "d": f.get("life", ""),
                    "x": f.get("role", ""),
                })
        except Exception as exc:  # noqa: BLE001
            print("  ! tokoh dilewati:", exc)

    js = "window.KRONIK_INDEX=" + json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (OUT / "assets" / "index-data.js").write_text(js, encoding="utf-8")
    return len(entries)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)

    for f in (ROOT / "assets").iterdir():
        if f.is_file():
            shutil.copy(f, OUT / "assets" / f.name)
    shutil.copytree(ROOT / "assets" / "fonts", OUT / "assets" / "fonts")

    global HAS_FIGURES
    try:
        figures = json.loads((DATA / "figures.json").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        figures = []
    HAS_FIGURES = bool(figures)

    chapters = load_chapters()
    if not chapters:
        raise SystemExit("Tidak ada bab di content/")
    print(f"  {len(chapters)} bab")

    (OUT / "index.html").write_text(build_index(chapters), encoding="utf-8")
    for ch in chapters:
        (OUT / ch["file"]).write_text(build_chapter(ch, chapters), encoding="utf-8")
    (OUT / "kronologi.html").write_text(build_timeline(chapters), encoding="utf-8")
    (OUT / "glosarium.html").write_text(build_glossary(chapters), encoding="utf-8")
    if HAS_FIGURES:
        (OUT / "tokoh.html").write_text(build_figures(figures, chapters), encoding="utf-8")
    (OUT / "tentang.html").write_text(build_about(chapters), encoding="utf-8")
    (OUT / "404.html").write_text(build_404(chapters), encoding="utf-8")

    urls = ["", "kronologi.html", "glosarium.html", "tentang.html"] + [c["file"] for c in chapters]
    today = date.today().isoformat()
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append(f"<url><loc>{SITE_URL}{u}</loc><lastmod>{today}</lastmod></url>")
    sitemap.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + SITE_URL + "sitemap.xml\n", encoding="utf-8")

    n = build_search_index(chapters)
    print(f"  indeks pencarian: {n} entri")

    total = sum(c["words"] for c in chapters)
    print(f"  {total} kata total")
    for p in sorted(OUT.glob("*.html")):
        print(f"  · {p.name}")


if __name__ == "__main__":
    main()
