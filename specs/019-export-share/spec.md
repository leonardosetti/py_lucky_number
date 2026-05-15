# Feature Specification: Export & Share

**Feature Branch**: `019-export-share`
**Created**: 2026-05-14
**Status**: Draft
**Input**: Exportação de combinações nos formatos CSV, JSON, PDF e compartilhamento via WhatsApp, e-mail entre usuários e cópia para área de transferência (Constitution Princípio VI).

---

## 1. Technical Overview

Implementar a exportação de combinações (histórico e resultado atual) nos formatos CSV, JSON e PDF, além de compartilhamento via WhatsApp (`wa.me`), e-mail entre usuários registrados e cópia para área de transferência. Cada operação respeita o escopo do usuário autenticado (apenas suas próprias combinações).

---

## 2. Behavior

- Export endpoints MUST require authentication (JWT).
- Each user exports only their own combinations.
- Share links MUST have configurable expiration (default 7 days).
- CSV and JSON exports are generated server-side.
- PDF export uses a server-side renderer.
- WhatsApp sharing generates a `wa.me` deep link with pre-formatted message.

---

## 3. User Scenarios & Testing *(mandatory)*

### User Story 1 — Export Combinations as CSV/JSON/PDF (Priority: P1)

**Acceptance Scenarios**:

1. **Given** an authenticated user with saved combinations, **When** they request `GET /api/v1/export/csv`, **Then** the response is a downloadable CSV file containing only that user's combinations.
2. **Given** the same user, **When** they request `GET /api/v1/export/json`, **Then** the response is a downloadable JSON array.
3. **Given** the same user, **When** they request `GET /api/v1/export/pdf`, **Then** the response is a downloadable PDF.

### User Story 2 — Share via WhatsApp (Priority: P2)

**Acceptance Scenarios**:

1. **Given** selected combinations, **When** the user clicks "Share via WhatsApp", **Then** a `wa.me` link is generated with the combination data pre-formatted as text message.
2. **Given** the generated link, **When** opened, **Then** it redirects to WhatsApp with the pre-filled message.

### User Story 3 — Share Between Registered Users (Priority: P2)

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they share a combination with another user by ID, **Then** the recipient receives a notification (spec 003) with the shared combination details.

### User Story 4 — Copy to Clipboard (Priority: P3)

**Acceptance Scenarios**:

1. **Given** selected combinations, **When** the user clicks "Copy", **Then** the combination data is formatted as text and returned via API for clipboard integration.

---

## 4. Functional Requirements

- **FR-001**: System MUST provide `GET /api/v1/export/csv` — export user's combinations as CSV.
- **FR-002**: System MUST provide `GET /api/v1/export/json` — export user's combinations as JSON.
- **FR-003**: System MUST provide `GET /api/v1/export/pdf` — export user's combinations as PDF.
- **FR-004**: System MUST generate `wa.me` links with pre-formatted message
  for WhatsApp sharing. Message format MUST be plain text listing each
  combination on a separate line with the game name and numbers, e.g.:
  `Mega-Sena: 03-12-23-34-45-56`
- **FR-005**: System MUST allow sharing combinations between registered users by recipient ID, with notification delivery.
- **FR-006**: System MUST provide `GET /api/v1/share/{id}/clipboard` — formatted text for clipboard copy.
- **FR-007**: Share links MUST expire after configurable TTL (default 7 days).
- **FR-008**: All export/share endpoints MUST require JWT authentication.
- **FR-009**: Users MUST only export/share their own combinations (user_id scoped).

---

## 5. Success Criteria *(mandatory)*

- **SC-001**: CSV export of 200 combinations completes in under 5 seconds.
- **SC-002**: JSON export completes in under 3 seconds.
- **SC-003**: PDF export completes in under 10 seconds.
- **SC-004**: WhatsApp link is generated in under 1 second.
- **SC-005**: Zero data leakage — no user can export another user's combinations.

---

## 6. Assumptions

- **PDF generation**: Uses a server-side library (ReportLab or WeasyPrint). No external API.
- **WhatsApp**: Uses `wa.me` deep link format — no official API key required.
- **Clipboard**: API returns formatted text; clipboard write is handled client-side.
- **Share between users**: Uses existing Notification system (spec 003) for delivery.
