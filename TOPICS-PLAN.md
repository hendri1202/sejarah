# Rencana Arsip — menuju 1.000+ artikel

Dua lapis situs: **26 bab** (narasi 3.000+ kata) + **arsip** (entri 800–1.100 kata).
Berkas entri: `content/entri/<id>.md`. Spesifikasi: `ENTRY-SPEC.md`.

## Klaster dan target

| # | Klaster | Target | Contoh isi |
|---|---|---|---|
| 1 | Vulkanologi & bencana | 45 | Krakatau, Tambora, Toba, Merapi, Kelud, tsunami, gempa, banjir |
| 2 | Geologi, karst, danau, laut | 30 | formasi batuan, karst Maros, Danau Poso, terumbu, arus |
| 3 | Arkeologi & situs prasejarah | 60 | Sangiran, Liang Bua, Gua Harimau, Buni, Toalean, megalit |
| 4 | Candi & prasasti | 65 | Borobudur, Prambanan, Singasari, Panataran, prasasti per prasasti |
| 5 | Kerajaan & kesultanan | 70 | Kutai, Sriwijaya, Mataram, Majapahit, Demak, Aceh, Banten, Gowa |
| 6 | Tokoh pra-1900 | 50 | raja, laksamana, ulama, pujangga |
| 7 | VOC & kolonial awal | 45 | kamar VOC, gubernur jenderal, monopoli, kota dagang |
| 8 | Tanam paksa & ekonomi kolonial | 50 | komoditas, cultuurstelsel, bank, kereta api, krisis |
| 9 | Perang & perlawanan | 55 | Padri, Diponegoro, Aceh, Bali, Maluku, Sulawesi |
| 10 | Politik etis, pers, pendidikan | 50 | sekolah, surat kabar, organisasi, kongres |
| 11 | Kota & arsitektur kolonial | 40 | Batavia, Bandung, Surabaya, Semarang, Medan |
| 12 | Pendudukan Jepang | 35 | kampanye militer, romusha, interniran, PETA, BPUPKI |
| 13 | Revolusi & diplomasi 1945–1949 | 45 | pertempuran, perundingan, negara bagian, PDRI |
| 14 | Politik 1950–1965 | 40 | kabinet, pemilu, pemberontakan, Irian Barat |
| 15 | Orde Baru | 50 | pemilu, dwifungsi, Timor Timur, pembangunan |
| 16 | Reformasi & Indonesia modern | 55 | amandemen, pemilu, otonomi, KPK, IKN |
| 17 | Ekonomi & bisnis | 50 | perusahaan, komoditas, kebijakan fiskal |
| 18 | Agama & organisasi | 40 | Islam, Kristen, Hindu-Buddha, pesantren, sinode |
| 19 | Budaya, seni, sastra, bahasa | 45 | wayang, batik, sastra, film, musik, bahasa |
| 20 | Sains, teknologi, kesehatan | 35 | observatorium, wabah, kedokteran, teknologi pangan |
| 21 | Militer & konflik | 40 | operasi, doktrin, konflik Papua, Aceh |
| 22 | Hukum & konstitusi | 35 | UUD, UU, pengadilan, kasus besar |
| 23 | Lingkungan & iklim | 30 | deforestasi, tambang, gambut, transisi energi |
| 24 | Historiografi, arsip, museum | 30 | sumber, metode, arsip, museum, penulisan sejarah |
| | **Total** | **1.025** | |

## Aturan penulisan gelombang berikutnya

1. Satu berkas = satu hal. Kalau judul mengandung "dan", pecah.
2. `id` unik, huruf kecil, tanda hubung, tanpa tahun di dalam id kecuali perlu (`krakatau-1883`).
3. `chapter` harus menunjuk bab yang benar-benar membahas konteksnya.
4. Jangan menulis topik yang sudah ada. Cek dengan `python3 tools/stats.py --ids`.
5. Setiap gelombang: 10 penulis × 15 entri = 150 entri.
6. Setelah tiap gelombang: build, audit tautan, commit, deploy.

## Status

Lihat `python3 tools/stats.py`.
