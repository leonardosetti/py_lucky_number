# Contracts: Apostador Registration Flow

**Phase**: 1 — Design & Contracts
**Date**: 2026-05-21

## API Endpoints

### POST /api/v1/auth/register

Register a new apostador account.

**Request**:
```json
{
  "nome": "Maria Silva",
  "email": "maria@email.com",
  "cpf": "529.982.247-25",
  "telefone": "+55 11 98765-4321",
  "data_nascimento": "1990-05-15",
  "senha": "Str0ng!Pass",
  "confirmacao_senha": "Str0ng!Pass",
  "canal_ativacao": "email",
  "enable_2fa": false,
  "captcha_token": "03AGdBq..."
}
```

**Success Response** (201 Created):
```json
{
  "user_id": "uuid",
  "message": "Conta criada com sucesso. Código de ativação enviado.",
  "activation_channel": "email",
  "activation_code_ttl": 86400
}
```

**Error Responses**:
- 400 Bad Request: Invalid input (CPF, email, password, etc.)
- 409 Conflict: Email or CPF already registered
- 429 Too Many Requests: Rate limited (includes `Retry-After` header)

**Rate Limiting**: 30s min interval per IP, max 5 attempts per email/CPF per hour

### POST /api/v1/auth/verify

Verify activation code and activate account.

**Request**:
```json
{
  "user_id": "uuid",
  "code": "482931"
}
```

**Success Response** (200):
```json
{
  "message": "Conta ativada com sucesso.",
  "access_token": "jwt...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "nome": "Maria Silva",
    "email": "maria@email.com",
    "cpf": "529.982.247-25",
    "status": "active"
  }
}
```

**Error Responses**:
- 400: Invalid or expired code
- 429: Too many attempts (max 5 = code invalidated)

### POST /api/v1/auth/resend-code

Resend activation code (invalidates previous code).

**Request**:
```json
{
  "user_id": "uuid",
  "canal": "sms"
}
```

**Success Response** (200):
```json
{
  "message": "Novo código enviado.",
  "activation_channel": "sms"
}
```

### GET /api/v1/profile

Get authenticated user's profile.

**Headers**: `Authorization: Bearer <jwt>`

**Success Response** (200):
```json
{
  "id": "uuid",
  "nome": "Maria Silva",
  "email": "maria@email.com",
  "cpf": "529.982.247-25",
  "telefone": "+55 11 98765-4321",
  "data_nascimento": "1990-05-15",
  "status": "active",
  "two_factor_enabled": true,
  "created_at": "2026-05-21T10:00:00Z"
}
```

### PUT /api/v1/profile

Update user profile fields (all except CPF).

**Request**:
```json
{
  "nome": "Maria Santos Silva",
  "telefone": "+55 11 97654-3210",
  "data_nascimento": "1990-05-15"
}
```

**Success Response** (200):
```json
{
  "message": "Perfil atualizado com sucesso.",
  "user": { "...updated fields..." }
}
```

**Note**: Changing email requires verification (see below).

### PUT /api/v1/profile/email

Request email change (sends verification code to new address).

**Request**:
```json
{
  "novo_email": "maria.novo@email.com"
}
```

**Success Response** (200):
```json
{
  "message": "Código de verificação enviado para o novo email.",
  "expires_in": 3600
}
```

### POST /api/v1/profile/email/verify

Confirm email change with verification code.

**Request**:
```json
{
  "novo_email": "maria.novo@email.com",
  "code": "739201"
}
```

**Success Response** (200):
```json
{
  "message": "Email atualizado com sucesso."
}
```

### PUT /api/v1/profile/password

Change password.

**Request**:
```json
{
  "senha_atual": "OldPass!1",
  "nova_senha": "NewStr0ng!Pass",
  "confirmacao": "NewStr0ng!Pass"
}
```

**Success Response** (200):
```json
{
  "message": "Senha alterada com sucesso."
}
```

### POST /api/v1/auth/2fa/setup

Initialize 2FA setup (returns QR code).

**Request**:
```json
{
  "method": "totp"
}
```

**Success Response** (200):
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,...",
  "uri": "otpauth://totp/LuckyNumber:maria@email.com?secret=...&issuer=LuckyNumber"
}
```

### POST /api/v1/auth/2fa/verify

Confirm 2FA setup with a TOTP code.

**Request**:
```json
{
  "code": "482931"
}
```

**Success Response** (200):
```json
{
  "message": "2FA ativado com sucesso.",
  "recovery_codes": ["xxxx-xxxx-xxxx", "yyyy-yyyy-yyyy", "zzzz-zzzz-zzzz"]
}
```

### POST /api/v1/auth/login (extended)

Login with optional 2FA challenge.

**Request**:
```json
{
  "email": "maria@email.com",
  "senha": "Str0ng!Pass"
}
```

**Success Response** (200) — without 2FA:
```json
{
  "access_token": "jwt...",
  "token_type": "bearer",
  "user": { "...user data..." }
}
```

**Success Response** (200) — with 2FA (requires second factor):
```json
{
  "requires_2fa": true,
  "session_token": "temp-session-token",
  "available_methods": ["totp", "biometric"]
}
```

### POST /api/v1/auth/2fa/verify-login

Complete 2FA challenge during login.

**Request**:
```json
{
  "session_token": "temp-session-token",
  "code": "482931"
}
```

**Success Response** (200):
```json
{
  "access_token": "jwt...",
  "token_type": "bearer",
  "user": { "...user data..." }
}
```

## Mobile-Specific Contracts

### POST /api/v1/auth/register/device

Register device fingerprint (called during mobile registration).

**Request**:
```json
{
  "device_hash": "sha256-of-device-fingerprint",
  "platform": "android",
  "attestation_token": "safetynet-or-appattest-token"
}
```

**Success Response** (200):
```json
{
  "device_id": "uuid",
  "trust_score": "high",
  "accounts_on_device": 1
}
```

**Error Response** (403):
```json
{
  "error": "Dispositivo não autorizado",
  "reason": "emulator_detected"
}
```

### POST /api/v1/auth/biometric/register

Register biometric key for 2FA (mobile only).

**Request**:
```json
{
  "biometric_public_key": "base64-encoded-public-key"
}
```

**Success Response** (200):
```json
{
  "message": "Biometria registrada com sucesso."
}
```

## Web Frontend Pages

| Route | Page | Description |
|-------|------|-------------|
| /register | RegisterForm | Registration form with all fields, CAPTCHA, channel selection |
| /activate/{user_id} | ActivationPage | Enter activation code, resend option |
| /profile | ProfilePage | View/edit profile, change password, 2FA settings |
| /login | LoginPage | Existing, extended with 2FA challenge flow |

## Mobile Screens

| Screen | Platform | Description |
|--------|----------|-------------|
| RegisterScreen | Both | Native registration form with input masks |
| ActivationScreen | Both | Code input with deep link support |
| ProfileScreen | Both | Native settings-style profile editor |
| SecurityScreen | Both | 2FA toggle, biometric setup, password change |
