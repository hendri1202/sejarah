# Spesifikasi Isi — Proyek "KRONIK"

Situs artikel sejarah berbahasa Indonesia. Setiap bab adalah satu file Markdown di `/opt/data/sejarah/content/`.
Bangun file HANYA untuk bab yang ditugaskan kepadamu. Jangan menyentuh file lain, jangan menjalankan build.

## Format file

Nama file: `NN-slug.md` (contoh: `01-dentuman-besar.md`).

```
---
number: 1
slug: dentuman-besar
part: bumi
title: Titik Nol
dek: Satu kalimat pengantar, maksimal 150 karakter, tanpa titik di akhir.
span: 13,8 miliar tahun lalu
dates:
  - "13,8 miliar tahun lalu|Dentuman Besar"
  - "380.000 tahun|Cahaya pertama memisah dari materi"
sources:
  - "Steven Weinberg, The First Three Minutes (1977)"
  - "NASA/WMAP Science Team, hasil pemetaan latar gelombang mikro kosmik"
---

Teks bab...
```

Aturan frontmatter:
- `part` salah satu: `bumi`, `manusia`, `kerajaan`, `kolonial`, `jepang`, `merdeka`.
- `dates`: 2–4 penanda waktu penting, format `"kapan|apa"`. `kapan` harus pendek (maks 32 karakter).
- `sources`: 2–4 rujukan NYATA dan umum dikenal (buku klasik, terbitan jurnal, museum, arsip). Jangan mengarang judul buku atau penulis. Kalau ragu, gunakan nama lembaga/terbitan yang jelas ada (mis. "Ricklefs, A History of Modern Indonesia since c. 1200", "National Museum of Indonesia", "Badan Geologi").
- Tanpa tanda kutip tambahan yang aneh; string berisi `:` atau `|` harus dalam tanda kutip ganda.

## Panjang & bentuk

- 900–1400 kata per bab. Padat, bukan bertele-tele.
- Mulai dengan adegan/Detail konkret (tempat, angka, benda, nama orang), bukan definisi kamus.
- 3–5 subjudul `## ` (maksimal 8 kata). Boleh `### ` sesekali.
- 1–2 kutipan tarik: baris yang diawali `> ` (maks 2 baris). Kalau mengutip orang, tulis atribusinya di baris berikutnya juga dengan `> `.
- 1–2 catatan margin, format persis:

```
:::note
Teks catatan pendek (maksimal 220 karakter). Boleh berisi angka pembanding.
:::
```

- Paragraf penutup yang menyambung ke bab berikutnya tanpa menyebut "bab berikutnya" secara literal.
- Tidak perlu daftar isi, tidak perlu ringkasan di akhir, tidak perlu bullet panjang. Daftar hanya untuk hal yang memang enumeratif (maks 5 butir).

## Suara penulisan (penting)

Tulis seperti sejarawan yang menjelaskan ke pembaca cerdas, bukan seperti mesin.

- Bahasa Indonesia baku, aktif, konkret. Hindari istilah Inggris bila ada padanan Indonesia.
- Angka pakai konvensi Indonesia: `13,8 miliar`, `4.540 juta tahun`, `abad ke-17`.
- Jangan memakai: "Dalam artikel ini", "Tahukah kamu", "Menariknya", "Selain itu" sebagai pembuka paragraf berulang, "Di sisi lain", "Mari kita", "Kesimpulannya", "Penting untuk dicatat".
- Jangan menebalkan frasa di tengah kalimat secara berlebihan. Maksimal satu penebalan per 300 kata, dan hanya untuk istilah teknis pertama kali muncul.
- Variasikan panjang kalimat. Boleh kalimat pendek sekali. Boleh satu paragraf hanya satu baris.
- Sebut angka yang spesifik, nama tempat, nama pelaku. Hindari generalisasi kosong seperti "banyak korban" bila angka perkiraan tersedia (sebutkan sebagai perkiraan).
- Kalau suatu hal masih diperdebatkan (misalnya angka korban, tanggal pasti, penafsiran), katakan bahwa itu perkiraan/debat. Jangan menyajikan dugaan sebagai fakta.
- Minimal satu tempat di setiap bab harus terasa lokal: nama situs, nama kampung, nama kapal, nama surat kabar, nama pasar, dan sebagainya.

## Akurasi

- Tanggal dan angka harus benar. Kalau ragu pada satu angka, gunakan rentang atau kualifikasi ("sekitar", "menurut perkiraan terbaru").
- Ejaan sejarah: gunakan ejaan sekarang untuk nama umum (Soekarno, Diponegoro, Sriwijaya), tetapi sebutkan ejaan lama bila relevan (Pithecanthropus erectus, Batavia).
- Jangan mengarang kutipan langsung. Kalau tidak yakin redaksi aslinya, parafrasa dan sebut sumbernya tanpa tanda kutip.
- Jangan memakai gambar, tautan eksternal, atau tabel.

## Markdown yang didukung

Hanya: paragraf, `## `, `### `, `> ` (kutipan tarik), `- ` (daftar pendek), `**tebal**`, `*miring*`, dan blok `:::note`. Jangan memakai tabel, gambar, HTML, atau heading level 1.
