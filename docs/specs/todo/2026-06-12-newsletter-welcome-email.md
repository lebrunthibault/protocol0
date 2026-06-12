# Newsletter welcome email on signup

> **Status: todo.** Blocked on a one-time manual prerequisite: verifying a sending domain in
> Resend (Domains → add `protocol0.live`, set the DKIM/SPF DNS records at the registrar). Until
> a domain is verified, Resend refuses to send to real recipients — the signup flow itself is
> unaffected and already live.

## Context

The landing page has a "Stay in the loop" section (`src/website/index.html#newsletter`) whose
form posts to `src/website/api/subscribe.js`, a Vercel serverless function that adds the contact
to the Resend audience **Protocol 0** (`RESEND_AUDIENCE_ID`, key in `RESEND_API_KEY` — both set
on the Vercel project for Production/Preview/Development). This is **single opt-in**: the only
feedback the subscriber gets is the on-page success message. No email is ever sent to them at
signup time.

Decided follow-up (option 2 of the opt-in discussion): keep single opt-in, but send a short
**welcome email** right after the contact is added. Full double opt-in (signed-token confirm
link + `api/confirm.js`) was considered and deliberately deferred — too much friction for a
beta waitlist; revisit only if the list grows or collects junk.

## Goal

When a visitor subscribes successfully, they receive a small welcome email within seconds:
"Welcome — you'll hear from me when something big ships." One email, no thread, no marketing.

Side benefit: a hard bounce on the welcome email flags typo'd/fake addresses in the audience.

## Implementation sketch

All in `src/website/api/subscribe.js` (~10 lines), after the contact-creation call succeeds:

- `POST https://api.resend.com/emails` with the same `RESEND_API_KEY` bearer:
  - `from`: a verified-domain address, e.g. `Protocol 0 <news@protocol0.live>` (new env var
    `NEWSLETTER_FROM` rather than hardcoding).
  - `to`: the subscribed email.
  - `subject` + minimal text/HTML body. Tone matches the site: confident, terse, no images.
  - Include a plain unsubscribe mention (transactional welcome emails don't get Resend's
    broadcast unsubscribe handling; a `mailto:` or one-line "reply to opt out" is enough).
- **Fire-and-forget semantics**: a failure to send the welcome email must NOT fail the
  subscription — the contact is already in the audience. Log via `console.error` and still
  return `200 {ok:true}`.
- Skip sending on the duplicate path (Resend 409 → already subscribed): no repeat welcome.
- Do not send for the honeypot path (already returns early).

## Acceptance

- Subscribing with a real address adds the contact AND delivers the welcome email.
- Re-subscribing the same address returns 200 and sends nothing.
- With `NEWSLETTER_FROM` unset or Resend `/emails` failing, subscription still succeeds (200,
  contact created), error visible in Vercel function logs.
- `src/website/README.md` Newsletter section updated: new env var, domain-verification
  prerequisite, welcome-email behavior.

## Prerequisites (manual, dashboard)

1. Resend → Domains → verify `protocol0.live` (DKIM/SPF records at the registrar).
2. Choose the sender address and set `NEWSLETTER_FROM` on the Vercel project (all three
   environments).
