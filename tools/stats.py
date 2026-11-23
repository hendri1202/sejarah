#!/usr/bin/env python3
"""Statistik arsip KRONIK: jumlah entri, sebaran, dan pemeriksaan duplikat."""
from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "content" / "entri"
CHAPTERS = ROOT / "content"


def read_meta(path: Path):
    raw = path.read_text(encoding="utf-8")
    meta = {}
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            for line in raw[3:end].splitlines():
                if ":" in line and not line.startswith("  -"):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
    return meta, raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", action="store_true", help="cetak semua id entri")
    ap.add_argument("--dupes", action="store_true", help="cari judul/id mirip")
    args = ap.parse_args()

    files = sorted(ENTRIES.glob("*.md"))
    ids = [f.stem for f in files]

    if args.ids:
        print("\n".join(ids))
        return 0

    eras = collections.Counter()
    tags = collections.Counter()
    chapters = collections.Counter()
    words = 0
    for f in files:
        meta, raw = read_meta(f)
        body = raw.split("---", 2)[2] if raw.count("---") >= 2 else raw
        words += len(re.findall(r"\w+", body))
        eras[meta.get("era", "?")] += 1
        chapters[meta.get("chapter", "?")] += 1
        for t in re.findall(r"[a-z0-9-]+", meta.get("tags", "")):
            tags[t] += 1

    print(f"entri: {len(files)} · kata: {words:,}".replace(",", "."))
    print("per era:", dict(sorted(eras.items())))
    print("per bab induk:", dict(sorted(chapters.items(), key=lambda kv: int(kv[0]) if str(kv[0]).isdigit() else 99)))
    print("topik terbanyak:", ", ".join(f"{t}({n})" for t, n in tags.most_common(12)))
    print(f"rata-rata kata: {words / max(1, len(files)):.0f}")

    if args.dupes:
        norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower())
        titles = []
        for f in files:
            meta, _ = read_meta(f)
            titles.append((f.stem, norm(meta.get("title", ""))))
        seen = {}
        for stem, title in titles:
            key = tuple(sorted(w for w in title.split() if len(w) > 3))
            if key in seen:
                print("mirip:", seen[key], "~", stem)
            seen[key] = stem
        dup_ids = [i for i, n in collections.Counter(ids).items() if n > 1]
        if dup_ids:
            print("id ganda:", dup_ids)

    ch_files = len(list(CHAPTERS.glob("*.md")))
    print(f"bab: {ch_files}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
