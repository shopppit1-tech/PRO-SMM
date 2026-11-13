import express from 'express';
import cors from 'cors';
import { createClient } from '@supabase/supabase-js';

const app = express();
const port = Number(process.env.PORT || 10000);
const peakerrUrl = (process.env.PEAKERR_API_URL || 'https://peakerr.com/api/v2').replace(/\/$/, '');
const usdToIdr = Number(process.env.USD_TO_IDR || 18258.97);
const frontendOrigin = process.env.FRONTEND_ORIGIN || '*';
const supabase = createClient(process.env.SUPABASE_URL || '', process.env.SUPABASE_ANON_KEY || '');

app.use(cors({ origin: frontendOrigin === '*' ? true : frontendOrigin, credentials: false }));
app.use(express.json({ limit: '32kb' }));

function requireConfig() {
  const required = ['PEAKERR_API_KEY', 'SUPABASE_URL', 'SUPABASE_ANON_KEY'];
  const missing = required.filter((key) => !process.env[key]);
  if (missing.length) throw new Error(`Server configuration missing: ${missing.join(', ')}`);
}

async function peakerr(action, params = {}) {
  requireConfig();
  const body = new URLSearchParams({ key: process.env.PEAKERR_API_KEY, action, ...params });
  const response = await fetch(peakerrUrl, {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded', accept: 'application/json' },
    body,
  });
  const data = await response.json().catch(() => null);
  if (!response.ok || (data && data.error)) {
    throw new Error(data?.error || `Peakerr returned HTTP ${response.status}`);
  }
  return data;
}

function idrRate(rate) {
  const value = Number(rate || 0) * usdToIdr;
  return Math.round(value);
}

function bearer(req) {
  const value = req.headers.authorization || '';
  return value.startsWith('Bearer ') ? value.slice(7) : '';
}

async function requireUser(req, res, next) {
  try {
    const token = bearer(req);
    if (!token) return res.status(401).json({ error: 'Login diperlukan.' });
    const { data, error } = await supabase.auth.getUser(token);
    if (error || !data.user) return res.status(401).json({ error: 'Sesi login tidak valid atau sudah kedaluwarsa.' });
    req.user = data.user;
    next();
  } catch (error) {
    res.status(401).json({ error: error.message });
  }
}

app.get('/health', (_req, res) => res.json({ ok: true, service: 'pro-smm-live-api' }));

app.post('/api/auth/signup', async (req, res) => {
  try {
    requireConfig();
    const { email, password } = req.body || {};
    if (!email || !password || String(password).length < 6) return res.status(400).json({ error: 'Email dan password minimal 6 karakter wajib diisi.' });
    const { data, error } = await supabase.auth.signUp({ email: String(email).trim(), password: String(password) });
    if (error) return res.status(400).json({ error: error.message });
    res.status(201).json({ user: data.user, session: data.session, message: data.session ? 'Akun aktif.' : 'Cek email untuk konfirmasi akun.' });
  } catch (error) { res.status(500).json({ error: error.message }); }
});

app.post('/api/auth/signin', async (req, res) => {
  try {
    requireConfig();
    const { email, password } = req.body || {};
    const { data, error } = await supabase.auth.signInWithPassword({ email: String(email || '').trim(), password: String(password || '') });
    if (error) return res.status(401).json({ error: error.message });
    res.json({ user: data.user, session: data.session });
  } catch (error) { res.status(500).json({ error: error.message }); }
});

app.get('/api/services', async (_req, res) => {
  try {
    const services = await peakerr('services');
    const live = Array.isArray(services) ? services.filter((item) => /facebook|youtube/i.test(`${item.category || ''} ${item.name || ''}`)).map((item) => ({
      ...item,
      rate_idr: idrRate(item.rate),
      currency: 'IDR',
      rate_basis: 'per 1000',
    })) : [];
    res.json({ services: live, count: live.length, usd_to_idr: usdToIdr });
  } catch (error) { res.status(502).json({ error: error.message }); }
});

app.post('/api/orders', requireUser, async (req, res) => {
  try {
    const { service, link, quantity, runs, interval } = req.body || {};
    const amount = Number(quantity);
    if (!service || !/^https?:\/\//i.test(String(link || '')) || !Number.isInteger(amount) || amount < 1) {
      return res.status(400).json({ error: 'service, link HTTPS/HTTP, dan quantity valid wajib diisi.' });
    }
    const result = await peakerr('add', { service: String(service), link: String(link), quantity: String(amount), ...(runs ? { runs: String(runs) } : {}), ...(interval ? { interval: String(interval) } : {}) });
    res.status(201).json({ provider: 'peakerr', user_id: req.user.id, result });
  } catch (error) { res.status(502).json({ error: error.message }); }
});

app.get('/api/orders/:orderId', requireUser, async (req, res) => {
  try {
    const result = await peakerr('status', { order: String(req.params.orderId) });
    res.json({ provider: 'peakerr', result });
  } catch (error) { res.status(502).json({ error: error.message }); }
});

app.listen(port, '0.0.0.0', () => console.log(`PRO-SMM live API listening on ${port}`));
