# Research Report: Apostador Registration Flow

**Phase**: 0 — Research & Unknowns Resolution
**Date**: 2026-05-21
**Feature**: Apostador Registration Flow (WEB + MOBILE)

## Resolved Unknowns

### 1. CAPTCHA Service

**Decision**: Google reCAPTCHA v3 (invisible) for web, Android SafetyNet/Play Integrity + iOS App Attest for mobile, with hCaptcha as fallback.

**Rationale**:
- reCAPTCHA v3 is invisible (no user interaction), highest conversion rate, well-documented React integration
- Mobile attestation (SafetyNet/App Attest) is required by Constitution Bloco 2 (security in UI)
- hCaptcha fallback for privacy-conscious users / GDPR/LGPD compliance concerns

**Alternatives considered**:
- reCAPTCHA v2 checkbox: Lower conversion, better accessibility — rejected because v3 handles both
- hCaptcha only: Higher latency, smaller ecosystem — kept as fallback
- Cloudflare Turnstile: Newer, less proven in Brazilian market — postponed

### 2. SMS/WhatsApp Delivery Provider

**Decision**: Twilio for both SMS and WhatsApp Business API delivery.

**Rationale**:
- Single provider for both SMS and WhatsApp — simplified integration and billing
- WhatsApp Business API support in Brazil (99%+ WhatsApp penetration)
- Reliable delivery tracking, webhook callbacks for delivery status
- Well-documented Python SDK (twilio), compatible with FastAPI async

**Alternatives considered**:
- AWS SNS: SMS only, no WhatsApp — rejected
- Zenvio (Brazilian provider): Good regional coverage but no WhatsApp API — rejected
- WhatsApp Business API directly: Requires more infrastructure setup — Twilio abstracts this

**Configuration**:
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` env vars
- `TWILIO_WHATSAPP_NUMBER` (+14155238886 or configured)
- `TWILIO_SMS_NUMBER` (Brazilian SMS-capable number)
- Rate: ~R$0.05/SMS, R$0.02/WhatsApp message (Brazil rates)

### 3. Email Transactional Service

**Decision**: Resend.com (resend) for transactional email delivery.

**Rationale**:
- Modern API-first approach, React Email integration for templates
- High deliverability in Brazil, DKIM/SPF configured per domain
- Python SDK (resend) with async support
- Free tier: 3,000 emails/month — sufficient for beta

**Alternatives considered**:
- SendGrid: Higher deliverability in BR but more complex setup — rejected for simplicity
- Amazon SES: Cheap but requires infrastructure setup — rejected
- SMTP direct: Unreliable delivery, IP reputation issues — rejected

### 4. 2FA/TOTP Implementation

**Decision**: pyotp library (backend TOTP generation), qrcode library (QR generation for authenticator setup).

**Rationale**:
- pyotp is the standard Python TOTP library, well-tested, compatible with Google Authenticator/Authy
- 30-second window, 6-digit codes, SHA-1 (standard TOTP)
- QR code generation via qrcode library + base64 PNG for web display

**Mobile alternative**: Biometric 2FA (Face ID / fingerprint) uses platform-native APIs:
- Android: BiometricPrompt API
- iOS: LocalAuthentication framework (LAContext)

### 5. CPF Validation Algorithm

**Decision**: Validate using the official Brazilian CPF algorithm (9 digits + 2 check digit verification) both client-side and server-side.

**Rationale**:
- The CPF algorithm is a public standard published by Receita Federal
- Client-side: immediate feedback, prevents unnecessary submission
- Server-side: mandatory validation, prevents bypass
- Implement as standalone utility `src/lucky_number/utils/cpf.py`
- Use known test CPFs for integration tests (049.314.559-27, etc.)

**Implementation approach**:
```python
def validate_cpf(cpf: str) -> bool:
    # Strip non-digits, validate length
    # Verify both check digits using modulo 11
    # Reject known invalid sequences (000.000.000-00, 111.111.111-11, etc.)
```

### 6. Activation Code Design

**Decision**: 6-digit numeric code, randomly generated via `secrets.randbelow(10**6)`, zero-padded to 6 digits.

**Rationale**:
- 6 digits = 1M possible combinations, sufficient for beta scale
- Numeric only: easy to type on phone keypad, no character confusion (0 vs O, 1 vs l)
- `secrets` module provides cryptographically secure randomness
- 5 attempt limit before code invalidation prevents brute force
- 24h TTL balances security (short enough to limit exposure) with UX (long enough for delayed email delivery)

### 7. Rate Limiting Strategy

**Decision**: Multi-layer rate limiting:
- **Layer 1 (IP-based)**: 30s delay between registration attempts from same IP (in-memory Redis)
- **Layer 2 (Email/CPF-based)**: Progressive delay: 30s → 60s → 120s → 300s → 600s for same email/CPF
- **Layer 3 (CAPTCHA)**: Required for every submission
- **Layer 4 (Cloud/CDN)**: WAF-level DDoS protection (Cloudflare or equivalent)

**Rationale**:
- Combines multiple signals to prevent abuse without punishing legitimate users
- IP-based delay prevents rapid-fire automated submissions
- Email/CPF-based progressive delay prevents targeted registration flooding
- CAPTCHA provides human verification layer
- CDN-level protection for volumetric DDoS

### 8. Mobile Push Notification for Activation

**Decision**: Use existing Firebase Cloud Messaging (FCM) for Android + Apple Push Notification Service (APNs) for iOS, integrated into the existing push infrastructure.

**Rationale**:
- FCM/APNs already assumed configured for the project (per spec 023 assumptions)
- Push notification includes deep link with activation context
- Code delivery via push is ~instant (< 5s) — best UX option
- Fallback to email/SMS/WhatsApp if push fails or user prefers

## Technology Choices

| Technology | Decision | Rationale |
|------------|----------|-----------|
| CAPTCHA | reCAPTCHA v3 + SafetyNet/App Attest | Best UX, platform-native |
| SMS/WhatsApp | Twilio | Single provider, Brazilian coverage |
| Email | Resend | Modern API, high deliverability |
| 2FA | pyotp + TOTP (back), Biometrics (mobile) | Standard, well-supported |
| CPF Validation | Custom implementation | Public algorithm, no external dependency |
| Activation Code | 6-digit numeric, secrets module | Secure, user-friendly |
| Rate Limiting | Multi-layer (IP, email/CPF, CAPTCHA) | Defense in depth |
