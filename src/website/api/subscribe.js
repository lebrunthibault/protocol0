// POST /api/subscribe — adds an email to the Resend audience for major-update announcements.
// Env vars (Vercel dashboard): RESEND_API_KEY, RESEND_AUDIENCE_ID.

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, company } = req.body || {};

  // Honeypot: real users never see the "company" field. Pretend success.
  if (company) return res.status(200).json({ ok: true });

  const value = typeof email === 'string' ? email.trim().toLowerCase() : '';
  if (!EMAIL_RE.test(value) || value.length > 254) {
    return res.status(400).json({ error: 'Invalid email address' });
  }

  const key = process.env.RESEND_API_KEY;
  const audience = process.env.RESEND_AUDIENCE_ID;
  if (!key || !audience) {
    console.error('subscribe: missing RESEND_API_KEY / RESEND_AUDIENCE_ID');
    return res.status(500).json({ error: 'Subscription failed' });
  }

  try {
    const r = await fetch(`https://api.resend.com/audiences/${audience}/contacts`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: value, unsubscribed: false }),
    });
    // 409 = already a contact: success from the visitor's point of view.
    if (r.ok || r.status === 409) return res.status(200).json({ ok: true });
    console.error('subscribe: Resend', r.status, await r.text().catch(() => ''));
    return res.status(500).json({ error: 'Subscription failed' });
  } catch (err) {
    console.error('subscribe:', err);
    return res.status(500).json({ error: 'Subscription failed' });
  }
}
