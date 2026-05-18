# Tasks — Lucky Number v0.1-beta

**Plan**: `.plan/v0.1-beta-plan.md` | **Specs**: 001–021
**Generated**: 2026-05-14 | **Total Tasks**: 187

---

## Phase 1: Setup — Project Initialization

**Goal**: Initialize project structure, dependencies, and tooling.

- [x] T001 Create directory structure per plan: `src/lucky_number/database/`, `src/collectors/`, `scripts/`, `tests/test_collectors/`, `web/`, `mobile/`
- [x] T002 [P] Update `pyproject.toml` with all dependencies: sqlalchemy, asyncpg, alembic, passlib, python-jose, orjson, polars, celery, redis, slowapi, prometheus-client. Remove `jinja2`.
- [x] T003 [P] Update `requirements-dev.txt` with pytest-asyncio, pytest-cov, respx, pytest-benchmark
- [x] T004 [P] Configure `setup.cfg` for flake8, isort, mypy, bandit
- [x] T005 [P] Configure `pyproject.toml` pytest section with `--cov-fail-under=90`
- [x] T006 [P] Initialize Alembic: `alembic init alembic` in `alembic/env.py`
- [x] T007 [P] Create `.env.dev`, `.env.demo`, `.env.prod` from `.env.example`
- [x] T008 [P] Update `Makefile` with targets: dev, test, coverage, lint, format, migrate, backup-build

---

## Phase 2: Foundational — Database, Auth & Feature Toggles (Specs 002, 003, 004)

**Goal**: PostgreSQL + SQLAlchemy + Alembic + JWT + bcrypt + Feature Toggles.
**Blocking**: All user stories depend on this phase.

### Database Engine & Core Models

- [x] T009 [P] Create `src/lucky_number/database/engine.py` with AsyncEngine, session factory, pool config (max 20), health check
- [x] T010 [P] Create `src/lucky_number/database/base.py` with SQLAlchemy declarative Base + `TimestampMixin` (created_at, updated_at)
- [x] T011 [P] Create `src/lucky_number/database/__init__.py` exporting engine and session
- [x] T012 [P] Create `src/lucky_number/database/models/__init__.py`

### Feature Toggles (Spec 002)

- [x] T013 [US1] Create `src/lucky_number/database/models/feature_toggle.py` — SQLAlchemy model with id, slug, nome, descricao, ativa, version (optimistic locking), timestamps
- [x] T014 [US1] Create `src/lucky_number/database/models/feature_toggle_audit.py` — immutable SQLAlchemy model for toggle change history
- [x] T015 [US1] Create `src/lucky_number/features/registry.py` — FeatureRegistry singleton with in-memory cache TTL 60s + invalidation
- [x] T016 [US1] Create `src/lucky_number/features/decorators.py` — `@require_feature(slug)` decorator returning 404 when inactive
- [x] T017 [US1] [P] Create `src/lucky_number/features/__init__.py`
- [x] T018 [US1] Create `GET /api/v1/admin/features` endpoint in `src/lucky_number/api/routes.py` — list all features
- [x] T019 [US1] Create `PUT /api/v1/admin/features/{slug}` endpoint — toggle feature with audit logging
- [x] T020 [US1] Create seed data script `scripts/seed.py` — insert initial features: geracao-apostas, promessas, export, admin

### Auth & Users (Spec 003)

- [x] T021 [US2] Create `src/lucky_number/database/models/user.py` — SQLAlchemy model with id, nome, email (unique), senha_hash, role_id (FK), regiao, ativo, timestamps, deleted_at (soft delete)
- [x] T022 [US2] Create `src/lucky_number/database/models/role.py` — SQLAlchemy model with id, nome (unique), descricao, parent_role_id (self-FK)
- [x] T023 [US2] Create `src/lucky_number/database/models/permission.py` — SQLAlchemy model with id, slug (unique), nome, recurso
- [x] T024 [US2] Create `src/lucky_number/database/models/role_permission.py` — SQLAlchemy association table with role_id, permission_id, granted
- [x] T025 [US2] Create `src/lucky_number/api/auth.py` — JWT middleware: `decode_jwt()`, `get_current_user()` dependency

- [x] T026 [US2] [P] Create `POST /api/v1/auth/register` — user registration with email validation, bcrypt hashing (cost 12)
- [x] T027 [US2] [P] Create `POST /api/v1/auth/login` — login returning JWT with user_id + role
- [x] T028 [US2] [P] Create `POST /api/v1/auth/refresh` — JWT refresh endpoint
- [x] T029 [US2] Create `POST /api/v1/auth/logout` — invalidate session

- [x] T030 [US2] [P] Create `GET /api/v1/admin/users` — list users with pagination, search, filters
- [x] T031 [US2] [P] Create `POST /api/v1/admin/users` — create user
- [x] T032 [US2] [P] Create `GET /api/v1/admin/users/{id}` — user detail
- [x] T033 [US2] [P] Create `PUT /api/v1/admin/users/{id}` — edit user
- [x] T034 [US2] [P] Create `DELETE /api/v1/admin/users/{id}` — soft delete with 2-step confirmation, block last admin, block self-deletion
- [x] T035 [US2] Create `POST /api/v1/admin/users/{id}/clone` — clone user with new ID

### Roles & Permissions (Spec 003)

- [x] T036 [US2] [P] Create `GET/POST /api/v1/admin/roles` — list and create roles
- [x] T037 [US2] [P] Create `GET/PUT/DELETE /api/v1/admin/roles/{id}` — read, update, delete role
- [x] T038 [US2] [P] Create `POST /api/v1/admin/roles/{id}/clone` — clone role with permissions
- [x] T039 [US2] Create `@require_permission(slug)` decorator in `src/lucky_number/api/dependencies.py`
- [x] T040 [US2] Create middleware blocking deletion of last admin user (implemented inline in T034)
- [x] T041 [US2] Create seed script for default roles (Admin, Auditor, TestDemo, Apostador) and permissions

### Rate Limiting & Security

- [x] T042 [US2] Configure slowapi rate limiter in `src/lucky_number/main.py` — disabled in test env
- [x] T043 [US2] Configure `CORSMiddleware` in `src/lucky_number/main.py` — disabled in test env
- [x] T044 [US2] Configure `TrustedHostMiddleware` in `src/lucky_number/main.py` — disabled in test env

### Migration & Lifecycle

- [x] T045 Create initial Alembic migration `alembic/versions/001_initial_schema.py` (manual)
- [x] T046 Update `src/lucky_number/main.py` with lifespan + security middleware

### Tests — Phase 2

- [ ] T047 [P] Write tests for `test_cache.py` with PostgreSQL fixture (requires DB running)
- [x] T048 [P] Write tests for `test_auth.py` — password hashing, JWT create/decode/validate
- [x] T049 [P] Write tests for `test_features.py` — model attributes, defaults, optimistic locking
- [x] T050 [P] Write tests for `test_roles.py` — model attributes, composite PK, defaults
- [ ] T051 [P] Write tests for `test_rate_limit.py` — 10 req/min enforcement (requires DB running)

---

## Phase 3: Promises, Notifications & Tracking (Specs 001, 003)

**Goal**: Bet promises with HMAC sharing, system notifications, usage dashboard.
**Depends on**: Phase 2 (Auth, Users, Database).

### Combinacoes Salvas (Spec 004, Principle IV)

- [x] T052 [US3] Create `src/lucky_number/database/models/combinacao.py` — model with id, user_id, jogo, dezenas[], dezenas_por_aposta, favorita, hash_combinacao (UNIQUE), created_at
- [x] T053 [US3] [P] Create `POST /api/v1/combinacoes` — save combination with hash verification, FIFO 200
- [x] T054 [US3] [P] Create `GET /api/v1/combinacoes` — list with pagination (20/page), filters: jogo
- [x] T055 [US3] [P] Create `DELETE /api/v1/combinacoes/{id}` — delete single or batch
- [x] T056 [US3] Create FIFO eviction logic in `src/lucky_number/services/combinacao_service.py` — remove oldest non-favorite when limit 200 reached, notify user
- [x] T057 [US3] Create notification mechanism for FIFO limit (200 combos) — via system notification

### Promises (Spec 001, Principle V)

- [x] T058 [US4] Create `src/lucky_number/database/models/promessa.py` — model with id, user_id, session_id, titulo, prioridade, valor_total, combinacoes_snapshot (JSONB), favorita, compartilhavel, hash_compartilhamento (unique), data_expiracao, created_at
- [x] T059 [US4] [P] Create `POST /api/v1/promessas` — create promise with snapshot, FIFO 50
- [x] T060 [US4] [P] Create `GET /api/v1/promessas` — list with pagination, filters (prioridade)
- [x] T061 [US4] [P] Create `DELETE /api/v1/promessas/{id}` — delete
- [x] T062 [US4] [P] Create `POST /api/v1/promessas/{id}/clone` — clone promise
- [x] T063 [US4] [P] Create `POST /api/v1/promessas/{id}/compartilhar` — generate HMAC sharing link
- [x] T064 [US4] Create FIFO eviction for promises (50 limit) in `src/lucky_number/services/promessa_service.py`

### Notifications (Spec 003)

- [x] T065 [US5] Create `src/lucky_number/database/models/notification.py` — SystemNotification and NotificationDelivery models
- [x] T066 [US5] [P] Create `POST /api/v1/admin/notifications` — admin endpoints
- [x] T067 [US5] [P] Create `GET /api/v1/notifications` — user's notifications with read/unread, pagination
- [x] T068 [US5] [P] Create `PUT /api/v1/notifications/{id}/read` — mark as read
- [ ] T069 [US5] Create auto-expiry logic for expired notifications (Celery Beat daily task)

### Usage Tracking & Dashboard (Spec 003)

- [x] T070 [US6] Create `src/lucky_number/database/models/usage_event.py` — model with id, user_id, session_id, event_type, metadata (JSONB), regiao, ip_hash, created_at
- [ ] T071 [US6] Create tracking middleware in `src/lucky_number/api/middleware.py` — auto-log events: login, generate, create_promise, feature_access
- [x] T072 [US6] [P] Create `GET /api/v1/admin/dashboard/summary` — aggregate metrics
- [x] T073 [US6] [P] Create `GET /api/v1/admin/dashboard/events` — filtered event list

### Audit Log (Spec 003)

- [x] T074 [US2] Create `src/lucky_number/database/models/audit_log.py` — immutable model
- [ ] T075 [US2] Create audit middleware in `src/lucky_number/api/middleware.py` — auto-log admin CRUD
- [ ] T076 [US2] Create `GET /api/v1/admin/audit-log` — query audit log with filters

### Alembic Migration — Phase 3

- [ ] T077 Create Alembic migration for: combinacoes_salvas, promessas, system_notifications, notification_deliveries, usage_events, audit_log

### Tests — Phase 3

- [ ] T078 [P] [US3] Write tests for `test_combinacoes.py`
- [ ] T079 [P] [US4] Write tests for `test_promises.py`
- [ ] T080 [P] [US5] Write tests for `test_notifications.py`
- [ ] T081 [P] [US6] Write tests for `test_dashboard.py`

---

## Phase 4: Data Collectors (Specs 007–017)

**Goal**: 10 collectors downloading CEF spreadsheets with Polars, storing in JSON + PostgreSQL.
**Depends on**: Phase 2 (Database engine).

### BaseCollector + Infrastructure

- [x] T082 Create `src/collectors/__init__.py`
- [x] T083 Create `src/collectors/base.py` — `BaseLotteryCollector` abstract class
- [x] T084 Create `src/collectors/utils.py` — HTTPX factory + retry
- [x] T085 Create Celery app in `src/tasks/celery_app.py`
- [ ] T086 Create `src/tasks/periodic.py` — Celery Beat schedule (requires Redis running)

### Collector Implementations (11 files)

- [x] T087 [P] [US7] Create `src/collectors/megasena.py` — MegasenaCollector
- [x] T088 [P] [US7] Create `src/collectors/lotofacil.py` — LotofacilCollector
- [x] T089 [P] [US7] Create `src/collectors/diadesorte.py` — DiadesorteCollector
- [x] T090 [P] [US7] Create `src/collectors/duplasena.py` — DuplasenaCollector
- [x] T091 [P] [US7] Create `src/collectors/quina.py` — QuinaCollector
- [x] T092 [P] [US7] Create `src/collectors/federal.py` — FederalCollector
- [x] T093 [P] [US7] Create `src/collectors/lotomania.py` — LotomaniaCollector
- [x] T094 [P] [US7] Create `src/collectors/timemania.py` — TimemaniaCollector
- [x] T095 [P] [US7] Create `src/collectors/maismilionaria.py` — MaismilionariaCollector
- [x] T096 [P] [US7] Create `src/collectors/supersete.py` — SuperseteCollector
- [x] T097 [P] [US7] Create `src/collectors/loteca.py` — LotecaCollector (critical window)

### Database Tables for Collectors

- [ ] T098 [P] Create Alembic migration for `loterias_resultados_megasena` with all columns per spec 007
- [ ] T099 [P] Create Alembic migrations for remaining 9 `loterias_resultados_{jogo}` tables (008–017)
- [ ] T100 [P] Create Alembic migration for audit logs (migrations_history, synthetic_data_generation_runs, database_performance_snapshots, backup_history)

### Tests — Phase 4

- [ ] T101 [P] Write `tests/test_collectors/test_base.py` — test BaseLotteryCollector abstract methods
- [ ] T102 [P] Write `tests/test_collectors/test_megasena.py` — parse, incremental update, error handling
- [ ] T103 [P] Write `tests/test_collectors/test_lotofacil.py` — same pattern
- [ ] T104 [P] Write tests for remaining 8 collectors
- [ ] T105 [P] Write `tests/test_celery.py` — Celery task execution, retry, schedule

---

## Phase 5: Infrastructure & DevOps (Specs 005, 006)

**Goal**: Docker multi-profile, Backup Go tool, CI/CD pipelines.
**Depends on**: Phase 2–4 (all core features implemented).

### Docker Compose (Spec 006)

- [x] T106 Refactor `docker-compose.yml` to multi-profile: dev, demo, test, prod
- [x] T107 [P] Add Redis service (all profiles)
- [x] T108 [P] Add Celery worker + Celery Beat services
- [x] T109 [P] Add named volumes: pgdata-dev, pgdata-demo
- [x] T110 Refactor `Dockerfile` to multi-stage with `USER appuser`
- [x] T111 Configure health check endpoint `/api/v1/health` (DB validation)

### Backup Tool (Spec 005 — Go)

- [x] T112 Create Go project structure: `scripts/backup-tool/` with dirs
- [ ] T113–T121 Implement Go backup tool (requires Go 1.22+ installed)
- [ ] T122 Create `scripts/build-backup.sh`

### CI/CD (Spec 006)

- [x] T123 Create `.github/workflows/ci.yml` — lint, test, security, migration dry-run
- [x] T124 Create `.github/workflows/cd.yml` — build once, deploy demo/prod
- [x] T125 [P] Configure semantic version tag (in cd.yml)
- [ ] T126 [P] Configure Trivy vulnerability scanner
- [ ] T127 [P] Configure Playwright E2E tests

### Observability

- [x] T128 Configure Prometheus metrics endpoint (`/metrics`)
- [x] T129 Expose collector metrics (Counters + Histograms in main.py)
- [x] T130 Add Prometheus + Grafana services (docker-compose prod profile)
- [ ] T131 Add Loki + Promtail services

### Tests — Phase 5

- [ ] T132 [P] Write integration tests for backup tool (mock pg_dump, test encryption/decryption cycle)
- [ ] T133 [P] Write tests for docker-compose multi-profile (verify each profile starts correct services)
- [ ] T134 [P] Write CI/CD workflow validation (dry-run on test.yml and deploy.yml)

---

## Phase 6: Export & Share (Spec 019)

**Goal**: CSV/JSON/PDF export + WhatsApp sharing + internal share + clipboard.
**Depends on**: Phase 3 (combinacoes_salvas, notifications).

- [ ] T135 [US8] Create `GET /api/v1/export/csv` — export user's combinations as CSV with headers
- [ ] T136 [US8] Create `GET /api/v1/export/json` — export user's combinations as JSON array
- [ ] T137 [US8] Create `GET /api/v1/export/pdf` — export user's combinations as PDF (ReportLab/WeasyPrint)
- [ ] T138 [US8] Ensure all export endpoints are scoped to authenticated user's own data only
- [ ] T139 [US9] Create `GET /api/v1/share/whatsapp/{id}` — generate `wa.me` link with plain text format
- [ ] T140 [US9] Create `POST /api/v1/share/user/{recipient_id}` — share combinations with other user via notification (spec 003)
- [ ] T141 [US9] Create `GET /api/v1/share/{id}/clipboard` — formatted text for clipboard copy
- [ ] T142 [US9] Implement share link expiry (7 days, configurable) in `src/lucky_number/services/share_service.py`

### Tests — Phase 6

- [ ] T143 [P] Write tests for `test_export.py` — CSV/JSON/PDF format validation, user isolation, empty state
- [ ] T144 [P] Write tests for `test_share.py` — WhatsApp link generation, user-to-user share, link expiry

---

## Phase 7: Web Frontend (Spec 020)

**Goal**: Responsive web app with data-testid, WCAG 2.2 AA, consuming API.
**Depends on**: Phase 2–6 (API endpoints implemented).

### Project Setup

- [ ] T145 Scaffold frontend project in `web/` using **Next.js 16** (framework definido via benchmark: Next.js vence em SSR, SEO, documentação Capacitor/mobile. SSR para páginas públicas, ISR para resultados de sorteios.)
- [ ] T146 [P] Configure ESLint, Prettier, Playwright in `web/`
- [ ] T147 [P] Configure CI job for frontend (lint + Playwright + Lighthouse)
- [ ] T148 [P] Create API client service in `web/src/services/api.ts` with JWT auth, CSRF, error handling

### Authentication Screens

- [ ] T149 [US10] Create Landing page — hero, feature cards, CTA
- [ ] T150 [US10] Create Login page — email + password, data-testid all elements
- [ ] T151 [US10] Create Register page — email + password + name, validation
- [ ] T152 [US10] Create "Try Anonymous" CTA — limited generate without login

### Core Screens

- [ ] T153 [US10] Create Generate page — game selector, quantity stepper (1–10), number picker, price preview, data-testid all elements
- [ ] T154 [US10] Create History page — paginated list (20/page), filter by game/date, favorite toggle, batch delete with confirmation, FIFO notification
- [ ] T155 [US10] Create Promises page — list, create from selection, share via WhatsApp, clone, delete
- [ ] T156 [US10] Create Notifications page — read/unread, pull-to-refresh
- [ ] T157 [US10] Create Profile page — name, email, change password, delete account (LGPD)
- [ ] T158 [US10] Create Empty State components — illustration + CTA for each list page

### Admin Screens

- [ ] T159 [US11] Create Admin Dashboard — aggregate metrics with charts, filters (user, role, region, date, value)
- [ ] T160 [US11] Create Feature Toggles page — switch list, audit log modal
- [ ] T161 [US11] Create User Management page — table with search, filter, clone, delete with 2-step confirmation

### Export & Accessibility

- [ ] T162 [US10] Add CSV/JSON/PDF download buttons to History and Promises pages
- [ ] T163 [US10] Implement responsive layout — bottom tabs (<768px), lateral drawer (>=768px)
- [ ] T164 [US10] Implement dark/light theme (follow system by default)
- [ ] T165 [US10] Add WCAG 2.2 AA compliance — ARIA labels, focus management, contrast, keyboard nav
- [ ] T166 [US10] Add axe-core audit to CI — zero violations gate

### E2E Tests — Phase 7

- [ ] T167 [P] Write Playwright test for login flow — register, login, session timeout redirect
- [ ] T168 [P] Write Playwright test for generate flow — select game, generate, save to history
- [ ] T169 [P] Write Playwright test for history — list, favorite, delete, FIFO notification
- [ ] T170 [P] Write Playwright test for admin — dashboard metrics, feature toggle, user CRUD
- [ ] T171 [P] Write Playwright test for responsive layout — 375px viewport, verify bottom tabs and touch targets

---

## Phase 8: Mobile App (Spec 021)

**Goal**: Android + iOS app with biometrics, offline, push, swipe.
**Depends on**: Phase 2–6 (API endpoints).

### Setup & Benchmark

- [ ] T172 Run benchmark to decide framework (React Native vs Kotlin/Compose + Swift/SwiftUI). Already defined: **nativo (Kotlin/Compose + Swift/SwiftUI)**. Versões mínimas: **Android API 26 (8.0)**, **iOS 15.0**. Cobertura Brasil: ~99% Android, ~95% iOS.
- [ ] T173 Scaffold mobile project in `mobile/` based on benchmark decision
- [ ] T174 [P] Configure CI for mobile (lint, build, test)
- [ ] T175 Create API client with certificate pinning + JWT in Keychain/Keystore

### Authentication & Biometrics

- [ ] T176 [US12] Create Login/Register screens with biometric opt-in
- [ ] T177 [US12] Implement Face ID / fingerprint authentication
- [ ] T178 [US12] Implement JWT storage in Keychain (iOS) / EncryptedSharedPreferences (Android)
- [ ] T179 [US12] Implement biometric fallback to password after 3 failures

### Core Features

- [ ] T180 [US12] Create Generate screen — game selector, quantity, numbers, price, swipe to dismiss results
- [ ] T181 [US12] Create History screen — paginated, swipe to delete, long press multi-select, pull-to-refresh
- [ ] T182 [US12] Create Promises screen — list, bottom sheet for create, share, clone
- [ ] T183 [US12] Create Notifications screen — list with read/unread, pull-to-refresh

### Offline & Push

- [ ] T184 [US12] Implement offline SQLite cache for lottery results, combinations, promises
- [ ] T185 [US12] Implement offline banner + queue operations for sync when online
- [ ] T186 [US12] Integrate FCM (Android) / APNs (iOS) for push notifications
- [ ] T187 [US12] Implement deep linking: `luckynumber://promise/{hash}`

### Admin Mobile

- [ ] T188 [US13] Create Admin Dashboard (adapted for mobile) — metrics + charts
- [ ] T189 [US13] Create Feature Toggles page (mobile-optimized)

### Platform-Specific

- [ ] T190 [P] iOS: Configure Apple HIG compliance, safe areas, dark mode
- [ ] T191 [P] Android: Configure Material Design 3, edge-to-edge, back gesture
- [ ] T192 [P] Configure app icons, splash screens, app store assets

### Tests — Phase 8

- [ ] T193 [P] Write Detox (RN) or XCUITest/Espresso E2E test for login with biometrics
- [ ] T194 [P] Write E2E test for offline cache + sync
- [ ] T195 [P] Write E2E test for swipe-to-delete gesture

---

## Phase 9: Polish & Cross-Cutting

**Goal**: Final testing, security audit, documentation, Termo de Aceite, deployment.

### Security Audit

- [ ] T196 Run OWASP ZAP scan against demo environment
- [ ] T197 Run bandit + safety + trivy scans — fix all HIGH findings
- [ ] T198 Verify no CWE-89/79/352/522 violations in all source code
- [ ] T199 Verify rate limiting (10 req/min) on /api/v1/gerar-apostas

### Documentation

- [ ] T200 Create `README.md` with project overview, setup instructions, architecture diagram
- [ ] T201 Create `CONTRIBUTING.md` with development workflow, PR template
- [ ] T202 Generate `TERMO_DE_ACEITE.md` — open source Terms of Service / EULA (Constitution VIII). Include: responsibilities, limitations, LGPD compliance, licensing (MIT/GNU), liability waiver for lottery result accuracy.

### Performance

- [ ] T203 Run hash lookup benchmark (<5ms with 100k+ records)
- [ ] T204 Run dashboard benchmark (<3s with 1M+ events)
- [ ] T205 Run Locust load test (100 concurrent users, 10 req/min each)

### Deployment

- [ ] T206 Deploy demo environment (auto from develop branch)
- [ ] T207 Deploy production (manual gate from main branch)
- [ ] T208 Verify pgBackRest backup + restore procedure

---

## Dependency Graph

```
Phase 1 (Setup)
   │
   ▼
Phase 2 (Database, Auth, Features) ──────────────────────┐
   │                                                      │
   ├──► Phase 3 (Promises, Notifications, Dashboard) ─────┤
   │                                                      │
   ├──► Phase 4 (Data Collectors) ────────────────────────┤
   │                                                      │
   ├──► Phase 5 (Infra, Docker, Backup, CI/CD) ───────────┤
   │                                                      │
   └──► Phase 6 (Export & Share) ◄────────────────────────┘
         │
         ▼
      Phase 7 (Web Frontend) ──── depends on API from Phases 2–6
         │
         ▼
      Phase 8 (Mobile App) ────── depends on API from Phases 2–6
         │
         ▼
      Phase 9 (Polish, Security, Docs, Deploy)
```

---

## Summary

| Phase | Tasks | Parallelizable | User Stories |
|---|---|---|---|
| 1 — Setup | 8 | 5 | — |
| 2 — Foundational | 43 | 20 | US1 (Features), US2 (Auth/Users) |
| 3 — Promises & Tracking | 30 | 12 | US3 (Combos), US4 (Promises), US5 (Notifs), US6 (Dashboard) |
| 4 — Data Collectors | 24 | 17 | US7 (Collectors) |
| 5 — Infra & DevOps | 29 | 12 | — |
| 6 — Export & Share | 10 | 2 | US8 (Export), US9 (Share) |
| 7 — Web Frontend | 27 | 6 | US10 (User Web), US11 (Admin Web) |
| 8 — Mobile App | 24 | 6 | US12 (User Mobile), US13 (Admin Mobile) |
| 9 — Polish | 13 | 3 | — |
| **Total** | **208** | **83 (40%)** | **13 user stories** |
