# Quickstart: Apostador Registration Flow

## Prerequisites

- Python 3.12+ environment with dependencies installed
- PostgreSQL 16+ running with migrations applied
- Redis 7+ running (for rate limiting + session cache)
- SMTP or Resend API key (for activation emails)
- Twilio account SID + auth token (for SMS/WhatsApp)
- reCAPTCHA v3 site key + secret key (for web CAPTCHA)

## Environment Variables

Add to `.env.dev`:

```bash
# CAPTCHA
RECAPTCHA_SITE_KEY=6Lc...
RECAPTCHA_SECRET_KEY=6Lc...

# Email (Resend)
RESEND_API_KEY=re_...

# SMS/WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_SMS_NUMBER=+5511999999999
TWILIO_WHATSAPP_NUMBER=+14155238886

# Rate Limiting
REGISTER_RATE_LIMIT_DELAY=30
REGISTER_MAX_ATTEMPTS_PER_HOUR=5

# Activation Code
ACTIVATION_CODE_TTL=86400
ACTIVATION_CODE_MAX_ATTEMPTS=5
```

## Database Migrations

```bash
# Generate new migration for registration tables
alembic revision --autogenerate -m "add_activation_registration_fields"

# Apply migration
alembic upgrade head
```

## API Testing

```bash
# Test registration flow
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Silva",
    "email": "maria@test.com",
    "cpf": "529.982.247-25",
    "telefone": "+55 11 98765-4321",
    "data_nascimento": "1990-05-15",
    "senha": "Str0ng!Pass",
    "confirmacao_senha": "Str0ng!Pass",
    "canal_ativacao": "email",
    "captcha_token": "test-token"
  }'

# Retrieve activation code from logs/email (dev mode)
# Verify activation
curl -X POST http://localhost:8000/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"user_id": "<user-id>", "code": "<code>"}'
```

## Test Accounts (Development)

| CPF | Name | Notes |
|-----|------|-------|
| 529.982.247-25 | Maria Silva | Valid CPF for testing |
| 049.314.559-27 | João Santos | Valid CPF for testing |
| 000.000.000-00 | - | Should be rejected (invalid) |

## Verification Checklist

- [ ] Registration form validates CPF client-side
- [ ] Registration form validates password strength client-side
- [ ] Registration form validates age >= 18 client-side
- [ ] Server rejects duplicate email/CPF
- [ ] Activation code is delivered via chosen channel
- [ ] Activation code expires after 24h
- [ ] Max 5 code attempts before invalidation
- [ ] Rate limiting blocks rapid registration attempts
- [ ] CAPTCHA required for form submission
- [ ] Auto-login after successful activation
- [ ] Profile page shows all fields, CPF read-only
- [ ] Password change works with current password validation
- [ ] Email change triggers verification to new address
- [ ] 2FA setup works with authenticator app
- [ ] Biometric 2FA works on mobile devices (if applicable)
