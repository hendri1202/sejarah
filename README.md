# Kronik — sejarah panjang bumi, manusia, dan Indonesia

Situs artikel sejarah berbahasa Indonesia: 26 bab, 6 bagian, dari Dentuman Besar sampai Indonesia hari ini.

- Isi: `content/*.md` (frontmatter + Markdown)
- Data: `data/timeline.json` (160 peristiwa), `data/glossary.json` (63 istilah)
- Tampilan: `assets/style.css`, `assets/app.js`, font lokal di `assets/fonts/`
- Pembangun: `build.py` → menghasilkan `docs/` (statis, siap GitHub Pages)

## Membangun

```bash
python3 build.py        # butuh paket markdown
```

Hasil ada di `docs/`. Buka `docs/index.html`, atau jalankan server lokal:

```bash
cd docs && python3 -m http.server 8000
```

## Struktur halaman

| Berkas | Isi |
|---|---|
| `index.html` | Sampul, tiga panel skala waktu, daftar isi 6 bagian |
| `01-…` s.d. `26-…` | Satu halaman per bab |
| `kronologi.html` | 160 peristiwa, bisa disaring per bagian |
| `glosarium.html` | 63 istilah, alfabetis |
| `tentang.html` | Catatan metode, batasan, kolofon, daftar bacaan |

Tanpa pelacak, tanpa iklan, tanpa dependensi JavaScript eksternal.
