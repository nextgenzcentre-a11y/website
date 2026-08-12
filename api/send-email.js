// api/send-email.js
//
// Server-side email dispatcher for NEXTGENZ CENTRE, backed by Resend.
// Vercel serverless function (Node.js runtime) - converted from the original
// Netlify function. Same logic, different handler signature.
//
// REQUIRED SETUP (do this once in the Vercel dashboard, never in code):
// Project -> Settings -> Environment Variables -> Add
//   Key:   RESEND_API_KEY
//   Value: <your Resend API key>
// Then redeploy (Vercel picks up env vars on the next deploy, same as Netlify).
//
// Also make sure your sending domain (nextgenzcentre.space) is verified under
// Resend -> Domains, or emails may get rejected/land in spam.

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method Not Allowed' });
    return;
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    // Fails loudly instead of silently - so a missing env var shows up immediately
    // in the portal's Email Alerts panel instead of emails quietly never arriving.
    res.status(500).json({
      message:
        'RESEND_API_KEY is not set. Add it under Vercel Project settings -> Environment Variables, then redeploy.'
    });
    return;
  }

  let body = req.body;
  // Vercel usually parses JSON bodies automatically, but guard against
  // it arriving as a raw string just in case.
  if (typeof body === 'string') {
    try {
      body = JSON.parse(body || '{}');
    } catch (e) {
      res.status(400).json({ message: 'Invalid JSON body' });
      return;
    }
  }
  body = body || {};

  const { from, to, reply_to, subject, html, text } = body;

  if (!to || (Array.isArray(to) && to.length === 0)) {
    res.status(400).json({ message: 'Missing "to" recipient' });
    return;
  }

  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: from || 'NEXTGENZ CENTRE <admission@nextgenzcentre.space>',
        to: Array.isArray(to) ? to : [to],
        reply_to: reply_to || 'nextgenzcentre@gmail.com',
        subject: subject || 'NEXTGENZ CENTRE Notification',
        html: html || (text ? `<p>${String(text).replace(/\n/g, '<br>')}</p>` : '<p>Empty body</p>'),
        text: text || undefined
      })
    });

    const resData = await response.json();

    if (!response.ok) {
      res.status(response.status).json({
        message: resData.message || 'Resend error',
        details: resData
      });
      return;
    }

    res.status(200).json({ success: true, data: resData });
  } catch (err) {
    res.status(500).json({ message: err.message || 'Server error' });
  }
}
