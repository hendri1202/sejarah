# Spesifikasi Isi — Proyek "KRONIK" (edisi rinci)

Situs artikel sejarah berbahasa Indonesia. Setiap bab adalah satu file Markdown di `/opt/data/sejarah/content/`.
Bangun file HANYA untuk bab yang ditugaskan. Jangan menyentuh file lain, jangan menjalankan build.

## Target: rinci, bukan ringkasan

- **3.000–3.800 kata per bab** (isi, bukan frontmatter).
- **8–12 subjudul `## `** (maksimal 8 kata), boleh `### ` untuk pecahan di dalamnya.
- **3–4 blok `:::note`** (catatan margin).
- **2–3 kutipan tarik** (`> `).
- **1 blok `:::linimasa`** berisi 6–9 baris `tahun|peristiwa` di bagian akhir bab.
- **5–6 `dates`** di frontmatter; **4–6 `sources`** nyata.

Kedalaman bukan berarti menambah kata sambung. Kedalaman berarti nama orang, nama tempat, angka, tanggal,
mekanisme sebab-akibat, dan perdebatan di antara sejarawan. Bab yang baik menjawab "bagaimana tepatnya"
dan "dari mana kita tahu".

## Bentuk wajib setiap bab

1. **Adegan pembuka** (150–250 kata): satu momen konkret — tanggal, tempat, orang, benda. Bukan definisi.
2. **Latar dan sebab** (2–3 subjudul): mengapa hal itu bisa terjadi, apa yang mendahuluinya.
3. **Proses/kronologi rinci** (3–5 subjudul): urutan peristiwa dengan tanggal dan nama, termasuk yang gagal.
4. **Angka dan bahan** (1–2 subjudul): jumlah, biaya, produksi, korban — dengan kualifikasi bila diperdebatkan.
5. **Perdebatan** (1 subjudul): apa yang masih diperselisihkan ahli, dan mengapa.
6. **Warisan/penutup** (100–180 kata): apa yang tersisa sampai sekarang, menyambung ke bab berikutnya.

Setiap bab wajib punya minimal satu **jangkar lokal Indonesia** (nama situs, kampung, kapal, pasar, surat kabar,
arsip, museum) dan minimal satu **angka spesifik yang mengejutkan tetapi benar**.

## Format file

Nama file sudah ada: jangan diganti. Tulis ulang isinya pada nama file yang sama.

```
---
number: 14
slug: voc
part: kolonial
title: Perusahaan dengan Pasukan Sendiri
dek: Satu kalimat, maksimal 150 karakter, tanpa titik di akhir
span: 1596 – 1799
dates:
  - "1596|Armada Houtman berlabuh di Banten"
  - "1619|Batavia berdiri"
sources:
  - "Femme Gaastra, The Dutch East India Company (2003)"
---

Teks bab...
```

Aturan frontmatter:
- `number`, `slug`, `part`, `title`, `span` **jangan diubah** (dipakai untuk URL dan urutan situs).
- `dek` boleh diperjelas, maksimal 150 karakter, tanpa titik di akhir.
- `part` hanya: `bumi`, `manusia`, `kerajaan`, `kolonial`, `jepang`, `merdeka`.
- `dates`: 5–6 penanda, format `"kapan|apa"`; `kapan` maksimal 32 karakter.
- `sources`: 4–6 rujukan NYATA (buku klasik, artikel jurnal, arsip, museum). Jangan mengarang judul atau penulis.

## Blok khusus

Catatan margin (3–4 per bab, maksimal 240 karakter):

```
:::note
Bandingkan dengan angka sensus 1930: ...
:::
```

Linimasa bab (tepat satu, di akhir, 6–9 baris):

```
:::linimasa
1825|Perang Jawa meletus di Tegalrejo
1830|Diponegoro ditangkap di Magelang
:::
```

Kutipan tarik: baris diawali `> `. Kalau mengutip orang, atribusinya ditulis di baris `> ` berikutnya.

## Suara penulisan

- Bahasa Indonesia baku, aktif, konkret. Angka pakai konvensi Indonesia: `13,8 miliar`, `Rp`.
- Nada sejarawan yang menjelaskan, bukan pemandu wisata. Tidak ada "Tahukah kamu", "Menariknya",
  "Dalam artikel ini", "Mari kita", "Kesimpulannya", "Penting untuk dicatat".
- Variasikan panjang kalimat dan paragraf. Boleh paragraf satu baris.
- Maksimal satu penebalan per 500 kata, hanya untuk istilah teknis yang pertama muncul.
- Sebut angka spesifik; kalau diperdebatkan, sebut rentang dan sumbernya.
- Jangan mengarang kutipan langsung. Kalau redaksi aslinya tidak terdokumentasi, parafrasa dan sebut sumbernya.
- Istilah asing dimiringkan, tetapi jangan berlebihan.

## Akurasi

- Tanggal dan angka harus benar. Verifikasi lewat pencarian web bila ragu (kamu punya alatnya).
- Kalau suatu angka adalah perkiraan, tulis "sekitar" atau "menurut perkiraan ...".
- Kalau ada dua versi yang beredar, tulis keduanya dan siapa yang mendukung.
- Bedakan jelas: sumber primer (prasasti, arsip, foto) vs sumber sekunder vs tradisi lisan.

## Markdown yang didukung

Paragraf, `## `, `### `, `> `, `- `, `**tebal**`, `*miring*`, `:::note`, `:::linimasa`.
Jangan memakai tabel, gambar, HTML, heading level 1, atau tautan eksternal.
