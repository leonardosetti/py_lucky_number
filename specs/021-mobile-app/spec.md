# Feature Specification: Mobile App

**Feature Branch**: `021-mobile-app`
**Created**: 2026-05-14
**Status**: Draft
**Input**: Primeira versão de implementação para UI/UX MOBILE do Lucky Number,
conforme Constitution Princípio VII (Cross-Platform App + UI/UX) e Bloco 2
(UI/UX — Mobile Implementation).

---

## 1. Technical Overview

Aplicativo mobile nativo para Android e iOS do sistema Lucky Number,
consumindo a mesma API REST do web frontend (spec 020). Compartilha
contratos de API, entidades e lógica de negócio com a versão web,
mas oferece experiência otimizada para dispositivos móveis: navegação
por bottom tabs, gestos (swipe), biometria, notificações push e suporte
offline parcial. A implementação pode ser nativa (Kotlin/Compose + Swift/SwiftUI)
ou multiplataforma (React Native), a definir após benchmark (Constitution VII).

**Gaps identificados em relação à Constitution e specs existentes**:

| Gap | Origem | Impacto |
|---|---|---|
| API de autenticação não implementada | Spec 003 | App não pode autenticar |
| APIs de domínio não implementadas | Specs 001–004 | Funcionalidades core indisponíveis |
| Push notifications sem backend | Spec 003 | Notificações não chegam em background |
| Offline storage sem schema definido | Spec 004 Bloco 3 | Cache local não implementado |
| Benchmark mobile não realizado | Constitution VII | Framework indefinido |

---

## 2. Behavior

### 2.1 Authentication & Security
- Register, login, JWT stored in **Keychain (iOS)** / **EncryptedSharedPreferences (Android)**
  — never plain SharedPreferences (CWE-522).
- Biometric authentication (Face ID / Touch ID / fingerprint) optional for
  quick login after initial authentication.
- Session timeout: 30 min inactivity (configurable). Anonymous TTL: 30 days.
- Certificate pinning for all API calls (prevents MitM).

### 2.2 Navigation
- **Bottom Tab Navigation** (Constitution VII): Home, Generate, History, Profile.
- Optional drawer menu for Admin section (when user has Admin role).
- Deep linking for shared promises: `luckynumber://promise/{hash}`.

### 2.3 Screens

#### Public (no auth)
- **Onboarding**: 3–4 screens highlighting key features (generate, save, share).
- **Login / Register**: Email + password. Biometric opt-in after first login.
- **Generate (guest)**: Limited to 1 generation, results shown once.

#### Authenticated
- **Home**: Recent activity, quick stats (total bets, active promises).
- **Generate**: Game selector, quantity (1–10), numbers, price preview.
  - Result: list with save-to-history or create-promise actions.
  - Swipe to dismiss individual results.
- **History** (`combinacoes_salvas`): Paginated (20), filter by game/date.
  - Swipe left to reveal delete action (Constitution VII).
  - Long press to multi-select for batch operations.
  - Favorite toggle.
  - FIFO notification at 200 limit.
- **Promises**: List with snapshot, share, clone, delete. FIFO at 50.
- **Notifications**: Pull-to-refresh. Swipe to mark as read. Tap to open detail.
- **Profile**: Name, email, change password. Biometric toggle. Delete account.
  - Theme toggle (light/dark) — follows system by default.

#### Admin
- **Dashboard**: Aggregate metrics with pull-to-refresh. Charts for trends.
- **Feature Toggles**: Switch list. Tap for audit log.
- **User Management**: Searchable table. Tap for detail/edit/clone/delete.

### 2.4 Offline Mode
- Historical lottery results cached locally (SQLite).
- User combinations, promises and notifications cached.
- Generate requires connectivity (validates against DB).
- Queue operations when offline: sync on reconnection.
- Show banner: "Você está offline. Os dados podem estar desatualizados."

### 2.5 Push Notifications
- New draw results available (when collectors update).
- Promises shared by other users.
- System notifications from admin.
- Daily reminder: "Que tal gerar seus números da sorte hoje?"

---

## 3. User Scenarios & Testing *(mandatory)*

### User Story 1 — User Registers with Biometrics (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a new user, **When** they open the app, **Then** an onboarding
   flow introduces the features, ending with Register or Login.
2. **Given** the registration form, **When** the user fills email + password
   and submits, **Then** the account is created, JWT stored in secure storage,
   and the user is prompted to enable biometrics.
3. **Given** a returning user with biometrics enabled, **When** they open
   the app, **Then** Face ID / fingerprint authenticates and the user lands
   on the Home screen without typing credentials.

### User Story 2 — User Generates and Saves Bets (Priority: P1)

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they tap the Generate tab,
   **Then** they see game selector, quantity stepper (1–10), and number picker.
2. **Given** selections made, **When** they tap "Generate", **Then** the system
   displays unique combinations with total price and a "Save All" button.
3. **Given** the result screen, **When** the user swipes left on a combination,
   **Then** a delete action is revealed (C7-required gesture support).
4. **Given** saved combinations approaching 200, **When** the user generates
   and saves 5 more, **Then** the app shows a toast: "5 combinações antigas
   foram removidas (limite de 200 atingido)."

### User Story 3 — User Manages Promises Offline (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a user with saved combinations, **When** they select 3 and tap
   "Create Promise", **Then** a bottom sheet appears to add title and priority.
2. **Given** promises exist, **When** the user goes offline, **Then** the
   promises list still displays from local cache.
3. **Given** the user creates a promise offline, **When** connectivity returns,
   **Then** the promise is synced to the server automatically.

### User Story 4 — Admin Monitors Dashboard (Priority: P2)

**Acceptance Scenarios**:

1. **Given** an admin, **When** they access the dashboard via the drawer menu,
   **Then** aggregate metrics are displayed with trend indicators.
2. **Given** the dashboard, **When** the user pulls down, **Then** the data
   refreshes with new metrics.

### User Story 5 — Push Notification for New Draw (Priority: P3)

**Acceptance Scenarios**:

1. **Given** push notifications enabled, **When** a new lottery draw is
   published by a collector, **Then** the user receives a notification:
   "Mega-Sena: novo sorteio disponível!"
2. **Given** the notification, **When** tapped, **Then** the app opens to
   the Generate screen with that game pre-selected.

---

### Edge Cases

- **Biometric failure**: Fallback to PIN / password. 3 consecutive failures
  lock biometric for the session.
- **Offline generation attempt**: Show "Geração requer conexão com a internet.
  Suas combinações serão validadas contra sorteios existentes."
- **Push notification permission denied**: App functions normally without
  push — notifications are visible in-app only.
- **Storage full (device)**: Show "Espaço insuficiente. Limpe o cache em
  Configurações > Armazenamento."
- **App backgrounded with unsaved data**: Auto-save draft to local storage.
  On reopen, prompt: "Você tem alterações não salvas. Continuar?"
- **Concurrent sessions**: Push notification to old device: "Sessão encerrada
  em outro dispositivo."

---

## 4. Functional Requirements

### Auth & Security
- **FR-001**: App MUST support registration and login via email + password.
- **FR-002**: JWT MUST be stored in Keychain (iOS) / EncryptedSharedPreferences
  (Android) — never plain storage (CWE-522).
- **FR-003**: App MUST support biometric authentication (Face ID / fingerprint)
  for quick login after initial auth.
- **FR-004**: App MUST implement SSL certificate pinning (CWE-295).

### Core Features
- **FR-005**: App MUST allow bet generation with game selector, quantity (1–10),
  and number picker with price preview.
- **FR-006**: App MUST save generated combinations to history with FIFO 200 limit
  and display notification when limit is reached.
- **FR-007**: App MUST allow viewing, filtering, favoriting, and deleting
  combinations from history.
- **FR-008**: App MUST support swipe-to-delete on list items.
- **FR-009**: App MUST support pull-to-refresh on data lists.
- **FR-010**: App MUST support long-press for multi-select.

### Promises (spec 001)
- **FR-011**: App MUST allow creating promises from selected combinations
  with title and priority via bottom sheet.
- **FR-012**: App MUST display promises list with snapshot values and
  support share, clone, delete operations.
- **FR-013**: App MUST enforce FIFO limit of 50 promises with notification.

### Notifications (spec 003)
- **FR-014**: App MUST display user notifications with read/unread status.
- **FR-015**: App MUST support push notifications for new draws, shares,
  and system messages.
- **FR-016**: App MUST allow admins to create/edit notifications (via drawer).

### Offline & Sync
- **FR-017**: App MUST cache lottery results, user history, promises, and
  notifications in local SQLite database.
- **FR-018**: App MUST queue operations when offline and sync when
  connectivity returns.
- **FR-019**: App MUST show offline banner when disconnected.
- **FR-020**: Generate operation MUST require connectivity.

### Admin (spec 002, 003)
- **FR-021**: App MUST display admin dashboard with aggregate metrics and
  pull-to-refresh.
- **FR-022**: App MUST allow toggling features with audit log view.
- **FR-023**: App MUST provide user management with search, filter, clone,
  and soft delete with 2-step confirmation.

### UI/UX & Platform
- **FR-024**: App MUST use bottom tab navigation (Constitution VII).
- **FR-025**: App MUST support light/dark theme following system setting.
- **FR-026**: Touch targets MUST be minimum 48x48dp (Material) / 44x44pt (iOS).
- **FR-027**: App MUST support deep linking: `luckynumber://promise/{hash}`.

---

## 5. Key Entities (Mobile)

- **UserSession**: JWT, user info, biometric enabled flag.
- **CachedCombination**: id, jogo, dezenas, favorita, hash, created_at
  (local SQLite copy — synced with API).
- **CachedPromise**: id, titulo, prioridade, valor_total, snapshot, favorita.
- **CachedNotification**: id, titulo, mensagem, lida, created_at.
- **OfflineQueueItem**: id, endpoint, payload, status (pending/synced/failed),
  created_at.
- **AppSettings**: biometric_enabled, theme (light/dark/system),
  push_enabled, session_timeout.

---

## 6. Success Criteria *(mandatory)*

- **SC-001**: User completes registration + biometric setup in under 3 minutes.
- **SC-002**: Bet generation completes in under 2 seconds on 4G.
- **SC-003**: History list loads 20 cached items instantly (offline),
  refreshes in under 2 seconds (online).
- **SC-004**: Swipe-to-delete gesture works on 100% of list items.
- **SC-005**: Biometric login authenticates in under 2 seconds.
- **SC-006**: Offline banner appears within 1 second of connectivity loss.
- **SC-007**: Push notification for new draw is delivered within 5 minutes
  of collector update.
- **SC-008**: All 5 main tabs load and display correct data.
- **SC-009**: FIFO notification appears when user hits 200 combinations /
  50 promises.
- **SC-010**: App renders correctly on iPhone SE (375x667), iPhone 14
  (390x844), Pixel 5 (393x851), and tablet 768x1024.

---

## 7. Assumptions

- **Framework**: **Nativo**: Kotlin/Compose (Android) + Swift/SwiftUI (iOS).
  Versões mínimas: **Android API 26 (8.0)** — ~99% cobertura Brasil;
  **iOS 15.0** — ~95% cobertura Brasil. Definição baseada em análise de
  mercado 2025–2026.
- **API compatibility**: Mesma API REST do web frontend (spec 020).
  Contratos e entidades são compartilhados.
- **Push notifications**: Requer serviço de push (FCM para Android,
  APNs para iOS, ou Expo Push para React Native). Implementação depende
  do framework escolhido.
- **Offline storage**: SQLite via Room (Android), WCDB/GRDB (iOS), ou
  expo-sqlite (RN). Schema espelha o backend apenas para leitura.
- **Deep linking**: Configuração de scheme `luckynumber://` em ambos
  os sistemas operacionais.
- **Biometrics**: BiometricPromise no Android (biometric prompt) e
  LocalAuthentication framework no iOS. Fallback para senha do app.
- **Certificate pinning**: SHA-256 hash do certificado do servidor
  embutido no código. Rotacionado via atualização do app.
