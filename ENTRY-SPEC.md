# Spesifikasi Entri Arsip — KRONIK

Situs ini punya dua lapis: **26 bab** (naratif panjang, 3.000+ kata) dan **Arsip** (entri fokus, 800–1.100 kata).
Kamu menulis entri arsip. Setiap entri adalah satu berkas Markdown di `/opt/data/sejarah/content/entri/`.

## Format berkas

Nama file: `<id>.md` — id sudah ditentukan, jangan diubah.

```
---
id: perang-padri
title: Perang Padri, 1803–1838
era: kolonial
years: 1803–1838
tags: [perang, sumatra, islam, minangkabau]
chapter: 16
dek: Satu kalimat, maksimal 150 karakter, tanpa titik di akhir
sources:
  - "Christine Dobbin, Islamic Revivalism in a Changing Peasant Economy (1983)"
  - "M.C. Ricklefs, A History of Modern Indonesia since c. 1200"
---

Teks entri...
```

Aturan:
- `id` harus sama dengan nama file (tanpa `.md`).
- `era` salah satu: `bumi`, `manusia`, `kerajaan`, `kolonial`, `jepang`, `merdeka`.
- `years`: rentang atau tahun, maksimal 24 karakter (mis. `1803–1838`, `1883`, `abad ke-14`).
- `tags`: 3–5 kata kunci huruf kecil, tanpa tanda kurung. Boleh format `[a, b, c]`.
- `chapter`: nomor bab induk (1–26), sudah ditentukan untuk tiap entri.
- `sources`: 3–4 rujukan NYATA.

## Bentuk entri

- **800–1.100 kata.** Fokus pada SATU hal: satu peristiwa, satu situs, satu tokoh, satu kebijakan, satu benda.
- **4–6 subjudul `## `** (maksimal 7 kata).
- **1–2 blok `:::note`** (catatan margin, maksimal 240 karakter).
- **1 kutipan tarik** (`> `), boleh kalimat penulis sendiri.
- Paragraf pembuka langsung ke hal konkret: tanggal, tempat, angka, nama. Tanpa definisi pembuka.
- Paragraf penutup pendek yang menyebut mengapa hal ini masih penting, atau apa yang belum terjawab.
- **Jangan mengulang ringkasan bab induk.** Entri harus menambah detail yang tidak ada di bab: angka,
  nama pelaku, kutipan arsip, mekanisme, atau perdebatan.
- Jangan memakai `:::linimasa` di entri (itu untuk bab).

## Suara

Bahasa Indonesia baku, aktif, konkret; nada sejarawan, bukan pemandu wisata. Larangan:
"Tahukah kamu", "Menariknya", "Dalam artikel ini", "Mari kita", "Kesimpulannya", "Penting untuk dicatat",
"Di sisi lain" sebagai pembuka paragraf. Maksimal satu penebalan per 500 kata.

Angka pakai konvensi Indonesia (`13,8 miliar`, `Rp`, `km`). Kalau angka diperdebatkan, tulis rentang
dan siapa yang mendukung. Jangan mengarang kutipan langsung. Jangan memakai tabel, gambar, HTML, atau tautan.

## Akurasi

Verifikasi tanggal dan angka lewat pencarian web bila ragu. Bedakan sumber primer (prasasti, arsip, foto)
dari sumber sekunder dan tradisi lisan. Kalau suatu klaim kontroversial, sebut bahwa itu kontroversial.
