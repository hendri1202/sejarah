#!/usr/bin/env python3
"""Validasi entri arsip KRONIK terhadap ENTRY-SPEC.md.

Pemakaian:
    python3 tools/validate.py            # semua entri
    python3 tools/validate.py --fix-list # hanya cetak daftar masalah ringkas
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRI = ROOT / "content" / "entri"
ERAS = {"bumi", "manusia", "kerajaan", "kolonial", "jepang", "merdeka"}
FORBIDDEN = ["tahukah kamu", "dalam artikel ini", "mari kita"]
FORBIDDEN_OPENERS = [
    r"(?:^|[.!?]\s+)Di sisi lain,",
    r"(?:^|[.!?]\s+)Menariknya",
    r"(?:^|[.!?]\s+)Kesimpulannya",
    r"(?:^|[.!?]\s+)Penting untuk dicatat",
]

def parse_front(text):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end < 0:
        return None, text
    raw = text[3:end].strip("\n")
    body = text[end + 4:]
    meta, key = {}, None
    for line in raw.splitlines():
        if re.match(r"^\s+-\s+", line) and key:
            meta.setdefault(key, []).append(re.sub(r"^\s+-\s+", "", line).strip().strip('"'))
            continue
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            meta[key] = val if val else []
    return meta, body

def check(path):
    text = path.read_text(encoding="utf-8")
    meta, body = parse_front(text)
    errs = []
    if meta is None:
        return ["frontmatter tidak ditemukan"]
    if meta.get("id") != path.stem:
        errs.append(f"id '{meta.get('id')}' != nama berkas")
    if not meta.get("title"):
        errs.append("title kosong")
    if meta.get("era") not in ERAS:
        errs.append(f"era tidak valid: {meta.get('era')}")
    yrs = meta.get("years", "")
    if not (1 <= len(yrs) <= 24):
        errs.append(f"years panjang {len(yrs)}")
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.strip("[]").split(",") if t.strip()]
    if not (3 <= len(tags) <= 5):
        errs.append(f"tags {len(tags)}")
    ch = meta.get("chapter", "")
    if not (str(ch).isdigit() and 1 <= int(ch) <= 26):
        errs.append(f"chapter tidak valid: {ch}")
    dek = meta.get("dek", "")
    if len(dek) > 150 or dek.endswith("."):
        errs.append(f"dek {len(dek)} char / titik akhir")
    srcs = meta.get("sources", [])
    if not isinstance(srcs, list) or not (3 <= len(srcs) <= 4):
        errs.append(f"sources {len(srcs) if isinstance(srcs, list) else '?'}")

    words = len(re.findall(r"\w+", body))
    if not (780 <= words <= 1150):
        errs.append(f"{words} kata")
    heads = re.findall(r"^##\s+(.+)$", body, re.M)
    if not (4 <= len(heads) <= 6):
        errs.append(f"{len(heads)} subjudul")
    if any(len(h.split()) > 7 for h in heads):
        errs.append("ada subjudul > 7 kata")
    notes = re.findall(r"^:::note\s*$", body, re.M)
    if not (1 <= len(notes) <= 2):
        errs.append(f"{len(notes)} note")
    for m in re.finditer(r":::note\s*\n(.+?)\n:::", body, re.S):
        if len(m.group(1).strip()) > 240:
            errs.append(f"note {len(m.group(1).strip())} char")
    if not re.search(r"^>\s+\S", body, re.M):
        errs.append("tanpa kutipan >")
    low = body.lower()
    for f in FORBIDDEN:
        if f in low:
            errs.append(f"frasa terlarang: {f}")
    for pat in FORBIDDEN_OPENERS:
        if re.search(pat, body):
            errs.append("pembuka terlarang: " + pat.split(')')[-1].strip())
    if re.search(r"^\|.*\|\s*$", body, re.M):
        errs.append("ada tabel")
    if re.search(r"!\[|<[a-z]+[\s>]|\]\(http", body):
        errs.append("ada gambar/HTML/tautan")
    return errs

def main():
    files = sorted(ENTRI.glob("*.md"))
    bad = {}
    for f in files:
        e = check(f)
        if e:
            bad[f.stem] = e
    print(f"entri: {len(files)} · bermasalah: {len(bad)}")
    for k, v in sorted(bad.items()):
        print(f"- {k}: {'; '.join(v)}")
    return 1 if bad else 0

if __name__ == "__main__" and "--sim" not in sys.argv:
    sys.exit(main())

# ————— deteksi kemiripan antar entri —————
def shingles(text, n=7):
    w = re.findall(r"\w+", text.lower())
    return {tuple(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}

def similarity_report(limit=25):
    from collections import defaultdict
    idx = defaultdict(set)
    files = sorted(ENTRI.glob("*.md"))
    texts = {}
    for f in files:
        meta, body = parse_front(f.read_text(encoding="utf-8"))
        sh = shingles(body)
        texts[f.stem] = sh
        for g in sh:
            idx[g].add(f.stem)
    pairs = defaultdict(int)
    for g, names in idx.items():
        if len(names) < 2 or len(names) > 40:
            continue
        names = sorted(names)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                pairs[(names[i], names[j])] += 1
    out = []
    for (a, b), n in pairs.items():
        base = min(len(texts[a]), len(texts[b])) or 1
        r = n / base
        if r > 0.04:
            out.append((r, a, b))
    out.sort(reverse=True)
    print(f"\nkemiripan antar entri > 4%: {len(out)} pasangan")
    for r, a, b in out[:limit]:
        print(f"- {r*100:.1f}%  {a} ↔ {b}")

if __name__ == "__main__" and "--sim" in sys.argv:
    similarity_report()
