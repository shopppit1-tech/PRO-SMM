# PRO-SMM

PRO-SMM adalah frontend katalog layanan Facebook dan YouTube yang terhubung ke backend live Render. Backend menyimpan API key Peakerr di environment server dan memakai Supabase Auth untuk login email.

## Live

- Frontend: `https://shopppit1-tech.github.io/PRO-SMM/`
- Backend health: `https://pro-smm-live-api.onrender.com/health`
- Katalog live: `https://pro-smm-live-api.onrender.com/api/services`
- Render Dashboard: `https://dashboard.render.com/web/srv-dbr7nl6tlv9c73fn4gag`

## Fitur backend

- `POST /api/auth/signup` — daftar email/password Supabase.
- `POST /api/auth/signin` — login email/password Supabase.
- `GET /api/services` — mengambil layanan Peakerr live dan menghitung `rate_idr`.
- `POST /api/orders` — mengirim order nyata ke Peakerr dengan Bearer token login.
- `GET /api/orders/:orderId` — membaca status order dari Peakerr.
- `GET /health` — health check Render.

Pesanan pada endpoint `/api/orders` adalah transaksi nyata dan memakai saldo akun Peakerr. Halaman frontend meminta login terlebih dahulu sebelum mengirim order.

## Environment backend

Lihat `.env.backend.example`. Secret wajib disimpan di Render Environment, bukan di GitHub Pages:

- `PEAKERR_API_KEY`
- `PEAKERR_API_URL`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `FRONTEND_ORIGIN`
- `USD_TO_IDR`

Katalog memakai kurs tampilan USD/IDR yang dikonfigurasi melalui `USD_TO_IDR`; kurs tersebut hanya untuk tampilan harga, bukan mekanisme pembayaran.
