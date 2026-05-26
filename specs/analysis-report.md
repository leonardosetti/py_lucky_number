# Specification Analysis Report — Project-Wide Consistency

**Generated**: 2026-05-23  
**Scope**: Full project (codebase, database, specs, constitution, plans)

---

## Critical Issues

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| I1 | Data Gap | CRITICAL | `user.py:12-27`, migration 001, spec 022 FR-001 | User model has 7 fields; spec 022 requires ~20+. Migration 001 doesn't reflect expanded schema. | **[RESOLVED]** Migration 002 created with all extensions (cpf, telefone, address, totp, etc). |
| I2 | Contradiction | CRITICAL | spec 025 FR-003/FR-004, spec 026 FR-004 | Spec 025 said "send recovery code" to email/WhatsApp; spec 026 said "send email with reset link only." Two different mechanisms. | **[RESOLVED]** Unified to link-based. 025 now says "reset link." 026 extended with FR-005 for WhatsApp delivery. |
| I3 | Missing Entity | CRITICAL | spec 026 Key Entities, migration 001, spec 004 | PasswordResetToken defined as key entity but no database table existed. | **[RESOLVED]** `password_reset_tokens` table created in migration 002 and spec 004. |
| I4 | Missing Infrastructure | CRITICAL | entire `src/`, spec 025 FR-006, spec 026 FR-004 | No email/SMS/WhatsApp sending capability existed. | **[RESOLVED]** `NotificationService` created with `EmailChannel` (SMTP), `WhatsAppChannel` (Twilio API), and `send_reset_link`/`send_activation_code` methods. |
| I5 | Missing Column | CRITICAL | `user.py:16-18`, migration 001, spec 025 FR-001, spec 026 FR-002 | User model had no `telefone` column. Specs 025 and 026 require phone for WhatsApp delivery. | **[RESOLVED]** `telefone`, `telefone_pais`, `telefone_verificado_em` added to User model + migration 002. |

## High Issues

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| I6 | Terminology Drift | HIGH | spec 024, 025, 026 titles | Three different names for same flow: "Forgot Password Link" / "Password Recovery Page" / "Password Reset API". | **[RESOLVED]** Specs reconciled. 025 uses "reset link" consistently. 026 references 025. |
| I7 | Naming Mismatch | HIGH | 025 "recovery code", 026 "email with link" | 025 said "Enviar código de recuperação" (send recovery CODE). 026 generates a LINK, not a code. | **[RESOLVED]** 025 button label changed to "Enviar link de recuperação." All references to "code" replaced with "link." |
| I8 | Scope Leak | HIGH | 026 spec.md, 025 spec.md FR-006 | Spec 025's submit action had no matching endpoint in 026. | **[RESOLVED]** `POST /auth/forgot-password` endpoint created matching 025's form (identifier + channel). |
| I9 | Missing Migration | HIGH | all migrations, spec 004 | Spec 004 had no auth-flow tables. | **[RESOLVED]** `password_reset_tokens` and `activation_codes` added to migration 002 and spec 004. |

## Medium Issues

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| I10 | No Plan/Tasks | MEDIUM | specs 024, 025, 026 | None of the 3 new specs had plan.md or tasks.md. | Pending — run `/speckit.plan` after spec reconciliation. |
| I11 | Route Prefix | MEDIUM | `routes.py:38-82`, spec 022 | Routes at `/auth/register` vs `/api/v1/auth/register` in specs. | Pending — align prefix across codebase. |
| I12 | No Redis | MEDIUM | `engine.py`, spec 004 FR-036 | No Redis session/anonymous session middleware. | Pending — constitution requires session support. |
| I13 | Missing Endpoints | MEDIUM | `routes.py` | No `/auth/forgot`, `/auth/reset`, `/auth/change-password`. | **[RESOLVED]** `POST /auth/forgot-password`, `GET /auth/reset-password`, `POST /auth/reset-password`, `POST /auth/change-password` created. |
| I14 | Phone in User | MEDIUM | spec 025, 022, `user.py` | WhatsApp delivery blocked without phone column. | **[RESOLVED]** `telefone` column added. |
| I15 | No Notification Service | MEDIUM | `src/lucky_number/services/` | Missing email/SMS/WhatsApp service. | **[RESOLVED]** `notification_service.py` created. |

## Coverage Summary

| Type | Count | Resolved | Pending |
|------|-------|----------|---------|
| CRITICAL | 5 | 5 | 0 |
| HIGH | 4 | 4 | 0 |
| MEDIUM | 5 | 3 | 2 |
| LOW | 4 | 0 | 4 |
| **Total** | **18** | **12** | **6** |

## Files Created/Modified

### New Files
- `alembic/versions/002_extend_user_add_auth_tables.py`
- `src/lucky_number/database/models/password_reset_token.py`
- `src/lucky_number/database/models/activation_code.py`
- `src/lucky_number/services/notification_service.py`

### Modified Files
- `src/lucky_number/database/models/user.py` — extended with 20+ profile fields
- `src/lucky_number/database/models/__init__.py` — added new model imports
- `src/lucky_number/api/routes.py` — added 4 new endpoints (forgot/reset/change password)
- `.env.example` — added SMTP, Twilio, notification config vars
- `specs/025-password-recovery/spec.md` — reconciled with 026 (link-based)
- `specs/026-password-reset-api/spec.md` — added WhatsApp delivery support
- `specs/026-password-reset-api/checklists/requirements.md` — updated status
- `specs/025-password-recovery/checklists/requirements.md` — updated status
- `specs/004-database-architecture/spec.md` — added auth tables, extended users

## Pending Items (not in scope of this analysis)
- Run `/speckit.plan` for specs 024, 025, 026
- API route prefix alignment (`/api/v1/` vs `/`)
- Redis session integration (constitution requirement)
- Low-severity items from TODO.md (spec 004 FR restoration, constitution outdated references, feature_toggles dedup)
