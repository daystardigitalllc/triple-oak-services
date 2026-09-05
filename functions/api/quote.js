// Cloudflare Pages Function - handles POST /api/quote from QuoteFunnel.astro
// and QuickQuoteBar.astro, sending the lead via Resend. Runs alongside the
// static Astro build with no adapter/output-mode change needed - Cloudflare
// picks up any file under functions/ automatically on the existing
// git-push-to-deploy pipeline.
//
// Requires a RESEND_API_KEY environment variable set in the Cloudflare
// Pages project (Settings -> Environment variables). Optional:
// RESEND_FROM_EMAIL (defaults to Resend's shared onboarding@resend.dev
// sender, which works without verifying a sending domain) and
// RESEND_TO_EMAIL (defaults to the business email in business.json).

const BUSINESS_NAME = 'Triple Oak Services';
const BUSINESS_EMAIL = 'info@tripleoakservices.com';

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

export async function onRequestPost({ request, env }) {
  const apiKey = env.RESEND_API_KEY;
  if (!apiKey) {
    return Response.json({ success: false, message: 'Email service is not configured yet.' }, { status: 500 });
  }

  const formData = await request.formData();

  // Honeypot: if the hidden field got filled, it's a bot - report success
  // without actually sending anything.
  if (formData.get('botcheck')) {
    return Response.json({ success: true });
  }

  const name = formData.get('name')?.toString().trim();
  const phone = formData.get('phone')?.toString().trim();
  const email = formData.get('email')?.toString().trim();

  if (!name || !phone || !email) {
    return Response.json({ success: false, message: 'Missing required fields.' }, { status: 400 });
  }

  const fields = [
    ['Name', name],
    ['Phone', phone],
    ['Email', email],
    ['Service', formData.get('service_requested')?.toString() || 'Not specified'],
    ['Street', formData.get('street')?.toString() || ''],
    ['City', formData.get('city')?.toString() || ''],
    ['Details', formData.get('details')?.toString() || ''],
  ].filter(([, value]) => value !== '');

  const htmlRows = fields
    .map(([label, value]) => `<tr><td style="padding:4px 12px 4px 0;font-weight:bold;vertical-align:top;">${label}</td><td style="padding:4px 0;">${escapeHtml(value)}</td></tr>`)
    .join('');

  const subject = formData.get('subject')?.toString() || `New Lead from ${BUSINESS_NAME}`;

  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: env.RESEND_FROM_EMAIL || `${BUSINESS_NAME} <onboarding@resend.dev>`,
        to: env.RESEND_TO_EMAIL || BUSINESS_EMAIL,
        reply_to: email,
        subject,
        html: `<table cellpadding="0" cellspacing="0">${htmlRows}</table>`,
      }),
    });

    if (!res.ok) {
      // Never return 502/504/520-527 from here - Cloudflare's edge treats
      // those as reserved origin-health signals and silently swaps in its
      // own generic branded error page instead of passing this JSON body
      // through, which is exactly what made this failure mode so opaque.
      const errorBody = await res.json().catch(() => null);
      return Response.json({ success: false, message: errorBody?.message || 'Failed to send.' }, { status: 500 });
    }

    return Response.json({ success: true });
  } catch {
    return Response.json({ success: false, message: 'Failed to send.' }, { status: 500 });
  }
}
