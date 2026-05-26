# Implementation Plan: Apostador Registration Flow (WEB + MOBILE)

**Branch**: `022-apostador-registration-flow` | **Date**: 2026-05-21 | **Spec**: specs/022-apostador-registration-flow/spec.md, specs/023-apostador-mobile-registration/spec.md
**Input**: Feature specification for apostador (better) user registration flow on web and mobile platforms.

## Summary

Implement a complete user registration flow for lottery players ("apostadores") on both web and mobile platforms. The feature covers: multi-field form (Nome, CPF, Data de Nascimento, Telefone, Email, Senha), strong password policy, CPF validation, age 18+ check, anti-flood/anti-DDoS with CAPTCHA, multi-channel activation code delivery (Email/SMS/WhatsApp/Push), email verification, optional 2FA (TOTP + Biometrics on mobile), auto-login after activation, and a user profile page where all fields except CPF are editable.

Backend APIs (auth/register, auth/login) already exist but must be extended to support the full CPF-based flow with pending activation state, activation codes, and profile management.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.x (web frontend), Kotlin 2.x (Android), Swift 5.9+ (iOS)  
**Primary Dependencies**:
- Backend: FastAPI, Pydantic v2, SQLAlchemy 2.0, asyncpg, passlib[bcrypt], python-jose, httpx
- Web: Next.js 16, React 19, Tailwind CSS
- Mobile: Kotlin/Compose (Android), Swift/SwiftUI (iOS)
- New dependencies: python-cpf-cnpj (CPF validation), pyotp (TOTP/2FA), qrcode (QR generation), twilio or similar (SMS/WhatsApp), email transactional service
**Storage**: PostgreSQL 16+ (users table extension, activation_codes table), Redis (rate limiting, session state, CAPTCHA verification)
**Testing**: pytest + pytest-asyncio (backend), @testing-library/react + Playwright (web), XCTest + XCUITest (iOS), JUnit + Compose Test (Android)
**Target Platform**: Web (latest 2 Chrome/Firefox/Safari/Edge), Android API 26+, iOS 15+
**Project Type**: Web application (Next.js frontend + FastAPI backend) + Native mobile apps
**Performance Goals**:
- Registration form validation feedback < 1s (client-side)
- Activation code delivery: email < 60s, SMS < 30s, WhatsApp < 10s, push < 5s
- Form submission processing < 2s under normal load
**Constraints**:
- Rate limiting: 30s delay between registration attempts from same IP, progressive for repeated attempts
- CAPTCHA required for all registration submissions
- Activation codes expire after 24h, max 5 attempts before invalidation
- CWE Top 25 compliance: CWE-20 (input validation), CWE-200 (no secrets in logs), CWE-522 (credential protection)
- LGPD compliance for Brazilian personal data (CPF, phone, birth date)
- Non-root containers, < 256MB memory per container
**Scale/Scope**: 10k registered users estimated in beta, ~100 new registrations/day peak

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principles Mapping

| Princípio | Status | Evidência |
|-----------|--------|-----------|
| **I. Data Integrity** | ✅ Not applicable | Registration flow does not involve combination generation |
| **II. User Privacy by Design** | ✅ Compliant | LGPD: soft delete, bcrypt + JWT, minimal data collection, CPF hashed in logs, right to be forgotten |
| **III. Controlled Random** | ✅ Not applicable | Registration flow only |
| **IV. User History** | ✅ Not applicable | Registration flow only |
| **V. Promises/Simulation** | ✅ Not applicable | Registration flow only |
| **VI. Export & Share** | ✅ Not applicable | Registration flow only |
| **VII. Cross-Platform App** | ✅ Implemented | Both web (spec 022) and mobile (spec 023) registration flows defined |
| **VIII. FOSS Licensing** | ✅ Compliant | All dependencies OSI-approved (bcrypt, TOTP, Twilio SDK, etc.) |

### Gates

- [x] **GATE 1**: Constitution principles reviewed — no violations found
- [x] **GATE 2**: Specs 022 and 023 exist and contain 0 [NEEDS CLARIFICATION] markers
- [x] **GATE 3**: Both specs checklists pass quality validation
- [ ] **GATE 4**: CPF validation algorithm implemented and tested — verify post-implementation
- [ ] **GATE 5**: Activation code delivery integrated with at least one external channel — verify post-implementation
- [ ] **GATE 6**: Rate limiting blocks automated mass-registration — verify with integration test

## Project Structure

### Documentation (this feature)

```text
specs/022-apostador-registration-flow/
├── spec.md              # Feature specification (WEB)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)

specs/023-apostador-mobile-registration/
├── spec.md              # Feature specification (MOBILE)
├── plan.md              # (linked from 022)
└── tasks.md             # (linked from 022)
```

### Source Code (repository root)

```text
src/lucky_number/
├── api/
│   ├── routes.py              # Extend with registration/activation/profile endpoints
│   ├── auth.py                # Extend with activation code verification
│   └── dependencies.py        # Rate limiting middleware
├── database/
│   ├── models/
│   │   ├── user.py            # Extend User model: CPF, phone, birth_date, status, 2fa_secret
│   │   └── activation_code.py # NEW: activation_codes table
│   └── engine.py
├── services/
│   ├── registration_service.py    # NEW: registration orchestration
│   ├── activation_service.py      # NEW: code generation, delivery, verification
│   ├── profile_service.py         # NEW: profile update with email verification
│   └── captcha_service.py         # NEW: CAPTCHA verification abstraction
├── config.py                 # Extend with external service configs
└── main.py                   # Extend with rate limiter, CORS

web/
├── src/
│   ├── app/
│   │   ├── register/            # NEW: registration page
│   │   ├── activate/            # NEW: activation code page
│   │   └── profile/             # NEW: profile management page
│   ├── components/
│   │   ├── RegisterForm.tsx     # NEW: registration form with validation
│   │   ├── ActivationInput.tsx  # NEW: activation code input component
│   │   ├── CpfInput.tsx         # NEW: CPF masked input with validation
│   │   └── PasswordStrength.tsx # NEW: password strength indicator
│   └── services/
│       └── api.ts              # Extend with registration/activation endpoints

mobile/
├── android/
│   └── app/src/main/java/com/luckynumber/
│       ├── ui/register/        # NEW: registration screens
│       └── ui/profile/         # NEW: profile screens
└── ios/
    └── LuckyNumber/
        ├── Views/Register/     # NEW: registration views
        └── Views/Profile/      # NEW: profile views

tests/
├── test_registration.py        # NEW: backend registration tests
├── test_activation.py          # NEW: activation code tests
├── test_profile.py             # NEW: profile management tests
├── test_cpf_validator.py       # NEW: CPF validation tests
└── test_rate_limiting.py       # NEW: anti-flood tests
```

**Structure Decision**: Hybrid — the existing project structure is preserved. New backend services and API routes are added following the established patterns. New web pages follow the Next.js App Router convention. Mobile additions follow platform conventions within the existing scaffold.

## Complexity Tracking

No constitution violations detected — complexity tracking not required.
