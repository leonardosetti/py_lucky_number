# Feature Specification: Web Frontend

**Feature Branch**: `020-web-frontend`
**Created**: 2026-05-14
**Last Updated**: 2026-05-26
**Status**: Draft
**Input**: Primeira versão de implementação para UI/UX WEB do Lucky Number,
conforme Constitution Princípio VII (Cross-Platform App + UI/UX) e Bloco 2
(UI/UX — Web Implementation).

---

## 1. Technical Overview

Interface web responsiva (mobile-first) para o sistema Lucky Number, consumindo
a API REST existente (spec 006). Disponibiliza todas as funcionalidades do
sistema: geração de apostas, histórico do usuário, promessas, notificações,
dashboard admin e exportação. Acessibilidade WCAG 2.2 AA, data-testid em todos
os elementos interativos, design responsivo nos breakpoints 320px–1440px.

**Gaps e dependências em relação à Constitution e specs existentes**:

| Dependência | Origem | Status |
|-------------|--------|--------|
| Autenticação JWT + registro/login | Spec 003, Spec 022 | ✅ Implementado |
| API `combinacoes_salvas` (CRUD + FIFO) | Spec 004 | ✅ Implementado |
| API `promessas` (CRUD + FIFO + share) | Spec 001 | ✅ Implementado |
| API notificações + delivery | Spec 003 | ✅ Implementado |
| Export CSV/JSON/PDF + WhatsApp share | Spec 019 | ✅ Implementado |
| Feature Toggles + audit | Spec 002 | ✅ Implementado |
| Password recovery (forgot/reset/change) | Specs 024–026 | ✅ Implementado |
| Coletores CEF (11 jogos) | Specs 007–017 | ⚠️ DB migrations pendentes |
| Dashboard admin + métricas agregadas | Spec 003 | Parcial — rotas existem, filtros combináveis pendentes |
| Cadastro com validação + ativação | Spec 022 | ✅ Implementado |
| Suporte a tema claro/escuro | Constitution Bloco 2 | Pendente no frontend |

**Estratégia**: Esta spec define o frontend MVP que consumirá os endpoints
da API independentemente do estado de implementação do backend. O frontend
deve tratar erros 501/503 graciosamente para funcionalidades ainda não
implementadas.

---

## 2. Behavior

### 2.1 Authentication Flow
- User can register (email + password) and login.
- JWT token stored in HttpOnly cookie (CWE-522).
- Session timeout after inactivity (configurable, default 30min).
- Anonymous mode: limited functionality (generate + view one-time results).

### 2.2 Navigation
- Bottom tab navigation on mobile (Constitution VII): Home, Generate, History, Profile.
- Lateral drawer on desktop (>768px): same items + Admin panel.
- Deep linking for shared promises (spec 001 FR-005).

### 2.3 Pages / Screens

#### Public (no auth required)
- **Landing/Home**: Hero, feature summary, call-to-action (register / try anonymous).
- **Login**: Email + password form. Link to register.
- **Register**: Email + password + name (optional). Email validation.
- **Generate (anonymous)**: Select game, numbers, generate, see results once.

#### Authenticated (user required)
- **Dashboard**: Recent activity, quick actions (generate, view promises).
- **Generate Bet**: Game selector (Mega-Sena, Lotofácil, etc.), number of bets (1–10),
  numbers per bet (game-dependent), price preview, generate button.
  - Result: list of generated combinations with option to save to history or
    create a promise.
- **My History** (`combinacoes_salvas`): Paginated list (20/page), filter by game,
  date, numbers. Favorite/unfavorite. Select for promise. Delete individual or batch.
  - Notification when approaching 200 limit (Constitution IV).
- **My Promises**: List of saved promises with snapshot. Share via WhatsApp link.
  Clone. Delete. Favorite/unfavorite.
- **Notifications**: List with read/unread status. Mark as read. Auto-expire.
- **Profile**: Name, email, change password. Delete account (LGPD right to erasure).

#### Admin (Admin role required)
- **Dashboard**: Aggregate metrics (active users, bets generated, promises created).
  Filters: user, role, region, date range, promise value range.
- **Feature Toggles**: List all features with on/off switch. Audit log of changes.
- **User Management**: CRUD table. Search, filter, clone, soft delete.
- **Notifications (admin)**: Create/edit/delete system notifications for users/roles.

---

## 3. User Scenarios & Testing *(mandatory)*

### User Story 1 — User Registers, Logs in and Generates Bets (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a new user on the landing page, **When** they click "Register"
   and fill email + password, **Then** the account is created and they are
   redirected to the authenticated dashboard.
2. **Given** an authenticated user, **When** they select Mega-Sena, 3 bets,
   6 numbers each, and click "Generate", **Then** the system displays 3 unique
   combinations with the total price, and an option to save to history.
3. **Given** an anonymous user, **When** they generate bets, **Then** results
   are shown once and cannot be saved (login prompt appears).

### User Story 2 — User Manages History with FIFO and Favorites (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a user with 200 saved combinations, **When** they generate 5 new
   bets and save them, **Then** the 5 oldest non-favorite combinations are
   removed, and a notification appears: "Limite de 200 combinações atingido.
   As 5 mais antigas foram removidas."
2. **Given** a user with saved combinations, **When** they toggle the favorite
   star on a combination, **Then** the star fills and the combination is marked
   as favorite (immune to FIFO eviction).
3. **Given** a user viewing their history, **When** they select multiple
   combinations and click "Delete", **Then** a confirmation dialog appears;
   after confirmation, the combinations are removed.

### User Story 3 — Admin Manages Features and Users (Priority: P1)

**Acceptance Scenarios**:

1. **Given** an admin logged in, **When** they access the admin panel,
   **Then** they see the dashboard with aggregate metrics (total users, bets,
   promises, most accessed features).
2. **Given** the admin panel, **When** the admin toggles a feature off,
   **Then** the feature is immediately disabled and the change is recorded
   in the audit log.
3. **Given** the user management screen, **When** the admin attempts to delete
   the last admin user, **Then** the system blocks the operation with an
   error message.

### User Story 4 — User Creates, Shares and Manages Promises (Priority: P2)

**Acceptance Scenarios**:

1. **Given** an authenticated user with saved combinations, **When** they
   select combinations and click "Create Promise", **Then** a modal appears
   to add title and priority; after saving, the promise appears in "My Promises".
2. **Given** a saved promise, **When** the user clicks "Share via WhatsApp",
   **Then** a `wa.me` link is generated with the combinations as plain text
   (spec 019 FR-004).
3. **Given** a user with 50 promises, **When** they create a new one,
   **Then** the oldest non-favorite promise is removed (FIFO) and a
   notification is shown.

### User Story 5 — Responsive Layout Adapts to Screen Size (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a 375px viewport (iPhone SE), **When** the page loads,
   **Then** all content is readable, touch targets are ≥48px, and bottom
   tab navigation is visible.
2. **Given** a 1024px viewport (desktop), **When** the page loads,
   **Then** the layout uses a lateral drawer instead of bottom tabs,
   and content uses multi-column grid layout.
3. **Given** any viewport, **When** tested with axe-core, **Then** no
   WCAG 2.2 AA violations are reported.

### User Story 6 — Data-testid Enables QA Automation (Priority: P2)

**Acceptance Scenarios**:

1. **Given** the login form rendered, **When** inspected by Playwright,
   **Then** the email input has `data-testid="email-input"`, the password
   input has `data-testid="password-input"`, and the submit button has
   `data-testid="login-submit-button"`.
2. **Given** a dynamic list of combinations, **When** the page renders
   20 items, **Then** each item has a unique `data-testid` based on its
   entity ID (e.g., `data-testid="combination-{id}-favorite-button"`).

---

### Edge Cases

- **Expired JWT**: User sees a session-expired modal and is redirected to
  login without losing their unsaved work (localStorage draft).
- **API 503 (feature not implemented)**: Frontend shows a friendly message:
  "Esta funcionalidade estará disponível em breve" with an estimated timeline.
- **Offline**: Show a banner "Você está offline. Algumas funcionalidades podem
  estar indisponíveis." Saved data in localStorage syncs when back online.
- **Rate limited (429)**: Show "Muitas requisições. Aguarde um momento."
- **Concurrent login same user**: Second login invalidates first session.
  First user sees "Sua sessão foi encerrada por outro login."
- **Empty states**: All list screens (history, promises, notifications) must
  show an empty state with illustration and CTA (e.g., "Você ainda não gerou
  nenhuma combinação. Que tal começar?").

---

## 4. Functional Requirements

### Core
- **FR-001**: System MUST provide a landing page with registration and login.
- **FR-002**: System MUST allow anonymous bet generation with one-time results.
- **FR-003**: System MUST provide an authenticated bet generation page with
  game selector, quantity (1–10), numbers per game, and price preview.
- **FR-004**: System MUST save generated combinations to user history
  (`combinacoes_salvas`) with FIFO limit of 200.
- **FR-005**: System MUST allow users to view, filter, favorite, and delete
  combinations from their history.
- **FR-006**: System MUST notify the user when approaching the 200-combination
  limit and when FIFO eviction occurs.

### Promises (spec 001)
- **FR-007**: System MUST allow users to create promises from selected
  combinations with title and priority.
- **FR-008**: System MUST display promises list with snapshot values.
- **FR-009**: System MUST allow sharing promises via WhatsApp `wa.me` link.
- **FR-010**: System MUST enforce FIFO limit of 50 promises per user.

### Notifications (spec 003)
- **FR-011**: System MUST display user notifications with read/unread status.
- **FR-012**: System MUST allow admins to create/edit/delete notifications
  for users and roles.

### Admin Dashboard (spec 003)
- **FR-013**: System MUST display aggregate metrics: total users, bets,
  promises, most accessed features.
- **FR-014**: System MUST support combinable filters: user, role, region,
  date range, promise value range.
- **FR-015**: System MUST display feature toggle list with on/off switch
  and audit log.
- **FR-016**: System MUST provide user CRUD with search, filter, clone,
  and soft delete with 2-step confirmation.

### Export (spec 019)
- **FR-017**: System MUST allow users to export their combinations as CSV.
- **FR-018**: System MUST allow users to export their combinations as JSON.
- **FR-019**: System MUST allow users to export their combinations as PDF.

### Testability & QA
- **FR-020**: Every interactive element MUST have a `data-testid` attribute.
- **FR-021**: Loading states MUST have `data-testid="loading-spinner"` or
  `data-testid="{component}-loading"`.
- **FR-022**: Error messages MUST have `data-testid="error-{context}"`.

### Accessibility & Responsive
- **FR-023**: All pages MUST pass WCAG 2.2 AA audit (axe-core, Lighthouse).
- **FR-024**: Layout MUST be responsive at 320px, 768px, 1024px, 1440px
  breakpoints with mobile-first approach.
- **FR-025**: Touch targets MUST be minimum 48x48px.
- **FR-026**: Navigation MUST use bottom tabs on mobile (<768px) and
  lateral drawer on desktop (≥768px).

### Security
- **FR-027**: JWT MUST be stored in HttpOnly cookie (CWE-522).
- **FR-028**: CSRF token MUST be included in all mutation requests (CWE-352).
- **FR-029**: Session MUST timeout after inactivity (configurable, default 30min).
- **FR-030**: Personal data testids MUST NOT expose real user IDs (use stable tokens).

---

## 5. Key Entities (Frontend Domain)

- **UserSession**: JWT token, user info (name, email, role), expiry.
- **Combination**: id, jogo, dezenas[], dezenas_por_aposta, favorita, hash,
  created_at (display only, fetched from API).
- **Promise**: id, titulo, prioridade, valor_total, combinacoes_snapshot,
  favorita, created_at.
- **Notification**: id, titulo, mensagem, prioridade, lida, created_at.
- **FeatureToggle**: slug, nome, descricao, ativa, version.
- **DashboardMetric**: Aggregate stats from admin API.
- **UserProfile**: nome, email, role, created_at.

---

## 6. Success Criteria *(mandatory)*

- **SC-001**: New user completes registration in under 2 minutes.
- **SC-002**: Bet generation result displays in under 2 seconds after click.
- **SC-003**: History page loads 20 items in under 1 second.
- **SC-004**: All 5 main flows (login, generate, history, promises, admin)
  work end-to-end.
- **SC-005**: Zero WCAG 2.2 AA violations on all pages (axe-core audit).
- **SC-006**: 100% of interactive elements have stable `data-testid`.
- **SC-007**: Layout renders correctly on iPhone SE, iPhone 12, iPad,
  Desktop 1280x720 and 1920x1080.
- **SC-008**: API errors (503, 429, 401) show user-friendly messages without
  breaking the UI.
- **SC-009**: FIFO notification is shown when limit is reached (200 combos,
  50 promises).

---

## 7. Assumptions

- **API endpoints**: Frontend assumes REST API at `/api/v1/` with JWT auth.
  Endpoints for each feature follow the conventions in specs 001, 002, 003,
  004, 019. Os fluxos de cadastro e recuperação de senha seguem as specs
  022–026. For features not yet implemented, the frontend shows a graceful
  "Em breve" message.
- **Language/framework**: **Next.js 16** (definido via benchmark). SSR para
  páginas públicas (landing, login, register), ISR para resultados de sorteios,
  SPA para painéis admin e dashboards.
- **data-testid convention**: Follows Constitution Bloco 2 — Web Implementation:
  `data-testid="{component}-{action}-{state}"`.
- **CSS approach**: CSS Modules or Tailwind. Mobile-first with `min-width`
  media queries. No IE11 support.
- **API error handling**: Backend returns `{ "detail": string, "status_code": int }`
  for all errors. Frontend maps status codes to user-friendly messages.
- **Offline detection**: `navigator.onLine` + `window.addEventListener('offline')`.
- **Session timeout**: Handled via JWT expiry. Frontend checks expiry before
  each API call and redirects to login if expired (saving draft in localStorage).
