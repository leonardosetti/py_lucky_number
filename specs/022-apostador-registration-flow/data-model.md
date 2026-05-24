# Data Model: Apostador Registration Flow

**Phase**: 1 — Design & Contracts
**Date**: 2026-05-21
**Feature**: Apostador Registration Flow (WEB + MOBILE)

## Entity: User (Apostador)

**Extends existing `users` table** — adding registration-specific fields.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique user identifier |
| nome | VARCHAR(255) | NOT NULL | Full name |
| email | VARCHAR(255) | NOT NULL, UNIQUE | Login email |
| cpf | VARCHAR(14) | NOT NULL, UNIQUE | Brazilian CPF (XXX.XXX.XXX-XX) |
| telefone | VARCHAR(20) | NOT NULL | Mobile phone (+55 XX XXXXX-XXXX) |
| data_nascimento | DATE | NOT NULL | Birth date (must be >= 18y ago) |
| senha_hash | VARCHAR(255) | NOT NULL | bcrypt hash (cost 12) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending, active, inactive, deleted |
| preferencia_canal | VARCHAR(20) | DEFAULT 'email' | Preferred activation channel: email, sms, whatsapp, push |
| two_factor_secret | VARCHAR(64) | NULLABLE | TOTP secret for 2FA (base32 encoded) |
| two_factor_enabled | BOOLEAN | DEFAULT false | Whether 2FA is active |
| biometric_enabled | BOOLEAN | DEFAULT false | Whether biometric 2FA is active (mobile only) |
| role_id | UUID | FK → roles | User role (default: apostador) |
| email_verified_at | TIMESTAMPTZ | NULLABLE | When email was last confirmed |
| last_login_at | TIMESTAMPTZ | NULLABLE | Last successful login |
| deleted_at | TIMESTAMPTZ | NULLABLE | Soft delete timestamp |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

### State Transitions

```text
[pending] ──[activate]──→ [active] ──[deactivate]──→ [inactive]
    │                                                    │
    └──[expire/24h]──→ [deleted]  ←────[reactivate]─────┘
```

- **pending**: Account created, awaiting activation code verification
- **active**: Account activated, full access
- **inactive**: Soft-deleted by admin (FR-008 from spec 022)
- **deleted**: Pending account that expired (24h TTL), auto-cleaned

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| nome | 2-255 chars, letters/spaces/accents only | "Nome inválido" |
| email | Valid email format, UNIQUE | "Email inválido" or "Email já cadastrado" |
| cpf | 11 digits, valid check digits, UNIQUE | "CPF inválido" or "CPF já cadastrado" |
| telefone | 10-11 digits, valid Brazilian mobile format | "Telefone inválido" |
| data_nascimento | Valid date, age >= 18 | "Você precisa ter 18 anos ou mais" |
| senha | Min 8 chars, uppercase, lowercase, digit, special | List missing requirements |
| confirmacao_senha | Must match senha | "Senhas não conferem" |

## Entity: Activation Code

**New table** `activation_codes` — tracks verification codes for account activation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK → users, NOT NULL | Target user for activation |
| code | VARCHAR(6) | NOT NULL | 6-digit numeric code |
| channel | VARCHAR(20) | NOT NULL | Delivery channel: email, sms, whatsapp, push |
| expires_at | TIMESTAMPTZ | NOT NULL | Code expiration (default: 24h from creation) |
| attempts | INTEGER | NOT NULL, DEFAULT 0 | Failed verification attempts |
| max_attempts | INTEGER | NOT NULL, DEFAULT 5 | Max allowed attempts |
| verified_at | TIMESTAMPTZ | NULLABLE | When code was successfully verified |
| invalidated_at | TIMESTAMPTZ | NULLABLE | When code was invalidated (reissue) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

### Constraints
- UNIQUE (user_id, code) — one active code per user at a time
- CHECK (attempts <= max_attempts)
- One active code per user (only one non-expired, non-verified, non-invalidated code)

### State Transitions

```text
[active] ──[verify]──────→ [used]
[active] ──[expire/24h]──→ [expired]
[active] ──[reissue]─────→ [invalidated]
```

## Entity: Registration Session (Mobile)

**Client-side only** — stored in encrypted local storage (Keychain/Keystore).

| Field | Type | Description |
|-------|------|-------------|
| session_id | UUID | Unique session identifier |
| form_data | Encrypted JSON | Partial registration form data |
| current_step | String | Registration flow step (form, activation, profile) |
| created_at | TIMESTAMP | Session creation time |
| expires_at | TIMESTAMP | Session expiration (30 min inactivity) |

## Entity: Device Fingerprint (Mobile)

**Server-side** — anonymous device identifier for anti-abuse.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| device_hash | VARCHAR(64) | NOT NULL, UNIQUE | SHA-256 hash of device fingerprint |
| account_count | INTEGER | NOT NULL, DEFAULT 1 | Number of accounts from this device |
| first_seen_at | TIMESTAMPTZ | NOT NULL | First registration from this device |
| last_seen_at | TIMESTAMPTZ | NOT NULL | Most recent registration |
| blocked | BOOLEAN | DEFAULT false | Whether device is blocked for abuse |

## Entity Relationships

```text
User (1) ──────→ (N) ActivationCode
  │
  └─────────────→ Role (N:1)
  
DeviceFingerprint (N) ←→ (M) User
  (via device_hash tracking)
```

## Indexes

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| users | email | UNIQUE | Fast login lookup |
| users | cpf | UNIQUE | Duplicate CPF detection |
| users | status | B-tree | List users by status |
| activation_codes | (user_id, expires_at) | Composite | Find active code per user |
| activation_codes | code | B-tree | Code verification lookup |
| device_fingerprints | device_hash | UNIQUE | Anti-abuse deduplication |
