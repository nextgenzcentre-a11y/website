// netlify/functions/send-email.js
//
// Server-side email dispatcher for NEXTGENZ CENTRE, backed by Resend.
// Replaces the old client-side EmailJS integration - the portal (index.html) now calls
// this function instead of talking to a third-party email SDK directly in the browser.
//
// REQUIRED SETUP (do this once in the Netlify dashboard, never in code):
//   Site settings -> Environment variables -> Add variable
//     Key:   RESEND_API_KEY
//     Value: <your Resend API key>
//   Then redeploy the site so the function picks it up.
//
// Also verify your sending domain (nextgenzcentre.space) under Resend -> Domains,
// or emails may get rejected/land in spam - see the note below.

exports.handler = async function (event) {
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method Not Allowed' })
    };
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    // Fails loudly instead of silently - so a missing env var shows up immediately in the
    // portal's Email Alerts panel instead of emails quietly never arriving.
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: 'RESEND_API_KEY is not set. Add it under Netlify Site settings -> Environment variables, then redeploy.'
      })
    };
  }

  let body;
  try {
    body = JSON.parse(event.body || '{}');
  } catch (e) {
    return { statusCode: 400, body: JSON.stringify({ message: 'Invalid JSON body' }) };
  }

  const { from, to, reply_to, subject, html, text } = body;

  if (!to || (Array.isArray(to) && to.length === 0)) {
    return { statusCode: 400, body: JSON.stringify({ message: 'Missing "to" recipient' }) };
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
      return {
        statusCode: response.status,
        body: JSON.stringify({ message: resData.message || 'Resend error', details: resData })
      };
    }

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ success: true, data: resData })
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ message: err.message || 'Server error' })
    };
  }
};
