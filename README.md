# Kronik — sejarah panjang bumi, manusia, dan Indonesia

Situs sejarah berbahasa Indonesia: **26 bab** naratif dan **arsip 1.401 entri** fokus, dari Dentuman Besar
sampai Indonesia 2026. Total sekitar **1.014.500 kata**.

Situs terbit: **https://hendri1202.github.io/sejarah/**

## Isi

| Bagian | Jumlah | Keterangan |
|---|---|---|
| Bab | 26 | Narasi 3.200–3.800 kata per bab; 6 bagian: Bumi, Manusia, Kerajaan, Kolonialisme, Perang & Pendudukan, Kemerdekaan |
| Entri arsip | 1.401 | 800–1.100 kata per entri: satu peristiwa, situs, tokoh, atau kebijakan |
| Kronologi | 160 peristiwa | Bisa disaring per bagian |
| Glosarium | 200 istilah | Geologi, arkeologi, kolonial, politik |
| Tokoh | 200 nama | Indeks dengan tautan ke bab asalnya |
| Topik | otomatis | Satu halaman per tag, dibuat dari frontmatter entri |
| Indeks A–Z | 1 halaman | Daftar abjad seluruh artikel arsip |
| Sumber & metode | 1 halaman | Tiga lapis sumber, angka diperdebatkan, tanggal resmi vs sejarah |
| Tanya | 1 halaman | Pencarian BM25 atas 612 dokumen, jawaban berkutip + tautan, fallback Wikipedia, mode LLM opsional |

## Struktur repositori

```
content/*.md            # 26 bab (frontmatter: number, slug, part, title, span, dates, sources)
content/entri/*.md      # entri arsip (frontmatter: id, title, era, years, tags, chapter, sources)
data/timeline.json      # 160 peristiwa
data/glossary.json      # 63 istilah
data/figures.json       # 80 tokoh
data/wave3.txt          # rencana topik gelombang berikutnya
assets/                 # CSS, JS, font woff2 (self-hosted), og.png
build.py                # pembangun: Markdown -> docs/ (statis)
docs/                   # keluaran, diterbitkan GitHub Pages
tools/stats.py          # statistik & cek duplikat entri
CONTENT-SPEC.md         # aturan penulisan bab
ENTRY-SPEC.md           # aturan penulisan entri
TOPICS-PLAN.md          # peta 24 klaster menuju 1.025 artikel
```

## Membangun

```bash
python3 build.py            # butuh paket `markdown`
cd docs && python3 -m http.server 8000
```

`build.py` menghapus `docs/` lalu membangun ulang seluruh halaman: 26 bab, 1.401 entri, halaman topik,
arsip, kronologi, glosarium, tokoh, tentang, 404, `sitemap.xml`, dan indeks pencarian.

Pemeriksaan sebelum terbit:

```bash
python3 tools/stats.py
python3 /opt/data/skills/software-development/editorial-content-site/scripts/audit_site.py docs content
```

## Prinsip isi

- Angka dan tanggal diverifikasi; yang diperdebatkan ditulis sebagai rentang beserta sumbernya.
- Tidak ada kutipan langsung yang dikarang. Kutipan hanya dipakai bila redaksinya terdokumentasi (mis. teks proklamasi).
- Tidak ada gambar; visual berupa tipografi, skala waktu, dan data.
- Tanpa pelacak, tanpa iklan, tanpa dependensi JavaScript eksternal.

## Penerbitan

- Repositori kerja: **hendri1202/history-app** (privat).
- Situs publik diterbitkan dari repositori cermin **hendri1202/sejarah**, GitHub Pages, sumber `main` / `docs`.
- Alasan pemisahan: GitHub Pages untuk repositori privat memerlukan paket berbayar, sedangkan isi dan riwayat
  kerja tetap privat di `history-app`.

## Lisensi

Teks ditulis untuk proyek ini. Rujukan pihak ketiga disebutkan per bab/entri dan tidak disalin isinya.
