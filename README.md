# PRO-SMM

Integrasi ringan untuk memuat katalog layanan dari API Peakerr ke `data/services.json`.

## Prasyarat

- Python 3.10 atau lebih baru.
- Akun Peakerr dengan API key. API key tidak disimpan di source code atau Git.

## Konfigurasi

Salin template environment, lalu isi key secara lokal:

```bash
cp .env.example .env
export PEAKERR_API_KEY="your-peakerr-api-key"
```

Atau gunakan environment manager pilihan Anda. Jangan commit file `.env`.

## Memuat layanan

```bash
python3 load_services.py --summary
```

Perintah ini melakukan `POST https://peakerr.com/api/v2` dengan `action=services` dan menyimpan respons array layanan ke `data/services.json`. Integrasi ini hanya membaca katalog; tidak ada endpoint order, pembayaran, atau perubahan akun yang dipanggil.

Endpoint dapat dioverride untuk pengujian:

```bash
export PEAKERR_API_URL="https://peakerr.com/api/v2"
```

## Struktur

- `peakerr_client.py` — client HTTP dan validasi respons API.
- `load_services.py` — CLI pemuat katalog.
- `data/` — output lokal; katalog hasil API diabaikan Git.
- `.env.example` — template konfigurasi tanpa kredensial.

## Catatan API

Percobaan tanpa key pada endpoint v2 terverifikasi mengembalikan `401 Invalid API key`. Karena itu, pemuatan katalog aktual baru dapat dijalankan setelah API key Peakerr tersedia di environment lokal atau secret deployment.
