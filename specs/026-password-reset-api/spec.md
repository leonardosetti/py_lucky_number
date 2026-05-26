# Feature Specification: Password Reset API

**Feature Branch**: `026-password-reset-api`  
**Created**: 2026-05-23  
**Status**: Draft  
**Input**: User description: "Crie a especificação para a api que vai realizar o reset de password do usuário, Para o reset funcionar o usuário deve existir na base, deve estar ativo, possuir email e telefone válidos, o reset de password deverá enviar um email com link que redirecionará para a pagina responsável pelo reset, o link deverá ter uma validade de 20 minutos, após este intervalo deve expirar, quando o usuário acessar o link deve setar uma nova senha e confirmar, então será redirecionado para a tela de login, na tela de login deverá fazer o login com a nova senha."

## User Scenarios & Testing

### User Story 1 — User successfully resets password via email link (Priority: P1)

As a registered user who forgot my password, I want to request a reset, receive an email with a secure link, set a new password, and log in again — all within a reasonable time window.

**Why this priority**: This is the complete happy-path flow that delivers the core value of the feature. Without it, users cannot recover their accounts.

**Independent Test**: A registered active user requests a password reset via email, receives the email within 2 minutes, clicks the link (within 20 minutes), enters a valid new password with confirmation, is redirected to the login page, and successfully logs in with the new password.

**Acceptance Scenarios**:

1. **Given** a registered active user with valid email and phone, **When** they submit a password reset request, **Then** the system generates a unique reset link and sends it to their registered email within 2 minutes.
2. **Given** the user received the reset email, **When** they click the link within 20 minutes of the request, **Then** they are presented with a new-password form where they can enter and confirm a new password.
3. **Given** the user enters a valid new password and confirmation, **When** they submit, **Then** the system updates their password, invalidates the reset link, and redirects them to the login page.
4. **Given** the user is on the login page with a newly reset password, **When** they enter their credentials with the new password, **Then** they successfully log in and access their account.

### User Story 2 — User clicks expired reset link (Priority: P1)

As a user who requested a password reset but took too long to act, I want to see a clear message that my link has expired, and be directed to request a new one.

**Why this priority**: Security requires link expiration; the user must understand why the link no longer works and how to proceed.

**Independent Test**: A user clicks a reset link 20+ minutes after the request, sees a clear expiration message with a link/button to request a new reset.

**Acceptance Scenarios**:

1. **Given** a user clicks a password reset link that was generated more than 20 minutes ago, **When** the system validates the link, **Then** the user sees a message: "Este link expirou. Solicite um novo link de redefinição de senha" (or equivalent), with a link to the password recovery page.
2. **Given** a user with an expired link clicks the "solicitar novo link" option, **When** they are redirected to the password recovery page, **Then** they can initiate a fresh reset request.

### User Story 3 — User tries to reuse a consumed reset link (Priority: P2)

As a security measure, a reset link that was already used must not be reusable, protecting the user from unauthorized password changes.

**Why this priority**: Security-critical — prevents token replay attacks. P2 because the happy path takes precedence but this is essential for a secure implementation.

**Independent Test**: A user completes a password reset via a link, then clicks the same link again and sees a message indicating the link has already been used.

**Acceptance Scenarios**:

1. **Given** a password reset link has already been used to successfully change a password, **When** someone clicks the same link again, **Then** the system displays a message: "Este link já foi utilizado. Solicite um novo reset de senha." (or equivalent).
2. **Given** a user sees the "already used" message, **When** they follow the prompt to request a new reset, **Then** they are taken to the password recovery page.

### User Story 5 — User requests password reset via WhatsApp (Priority: P1)

As a registered user who prefers WhatsApp, I want to receive the reset link on my phone via WhatsApp so that I can reset my password even without email access.

**Why this priority**: WhatsApp is a required delivery channel matching spec 025-password-recovery. Without it, users who identify via phone cannot complete recovery.

**Independent Test**: A user enters a registered phone, selects "enviar por WhatsApp", receives the reset link on WhatsApp within 2 minutes, clicks the link, sets a new password, and logs in.

**Acceptance Scenarios**:

1. **Given** a registered active user with a verified phone, **When** they submit a password reset request via WhatsApp, **Then** the system generates a reset link and sends it to their registered phone via WhatsApp within 2 minutes.
2. **Given** the user received the WhatsApp message with the reset link, **When** they click the link within 20 minutes, **Then** they are presented with the new-password form.
3. **Given** a user submits a reset request via WhatsApp for a phone that is not registered, **When** the system processes the request, **Then** it returns a generic success message (no enumeration leak).

### User Story 4 — Non-existent or inactive user attempts reset (Priority: P2)

As a security measure, the system must not reveal whether a given email belongs to a registered account, preventing user enumeration attacks.

**Why this priority**: Security best practice — prevents attackers from discovering registered emails. P2 because it does not block the happy path but is important for a production-grade feature.

**Acceptance Scenarios**:

1. **Given** an unregistered email is submitted for password reset, **When** the system processes the request, **Then** it returns a generic success message identical to the one shown for registered users.
2. **Given** a deactivated/blocked user's email is submitted for password reset, **When** the system processes the request, **Then** it returns a generic success message (same as for unregistered emails).

### Edge Cases

- **Multiple reset requests**: If a user requests multiple resets, only the latest link should be valid; previous links must be invalidated.
- **Link tampering**: If a user manually modifies the reset link parameters, the system must reject the link as invalid and show an appropriate error message.
- **Weak password**: If the new password does not meet strength requirements, show a validation error and allow the user to try a different password without requiring a new link.
- **Password mismatch**: If the password and confirmation do not match, show an inline validation error before submission.
- **Same as old password**: If the new password is the same as the current password, inform the user and require a different password.
- **Concurrent reset attempts**: If two reset requests are made within the same 20-minute window, only the most recent token should be valid.
- **Network failure on email send**: If the email fails to send (e.g., SMTP unavailable), the system must retry and, if persistent, notify an administrator. The user sees a generic success message (to avoid revealing system state).

## Requirements

### Functional Requirements

- **FR-001**: The system MUST expose a mechanism (API endpoint) to initiate a password reset given a user identifier (email or phone) and a delivery channel (email or whatsapp).
- **FR-002**: When a reset is requested, the system MUST validate that the user exists in the database, is active (not blocked/deactivated), and has both a valid email and a valid phone number on file. If any check fails, return a generic success message (no distinction between "user not found" and "invalid channel").
- **FR-003**: Upon successful validation, the system MUST generate a unique, cryptographically secure reset token associated with that user. The token MUST be single-use and must expire 20 minutes after generation.
- **FR-004**: When the delivery channel is `email`, the system MUST send an email to the user's registered email address containing a reset link. The link MUST include the reset token and redirect to the password reset page (to be implemented as the new-password form page).
- **FR-005**: When the delivery channel is `whatsapp`, the system MUST send the reset link via WhatsApp to the user's registered phone number. The message MUST contain the same reset link as the email version.
- **FR-006**: The system MUST expose a mechanism (API endpoint) to validate a reset token. It MUST reject tokens that are expired (>20 min), already used, tampered with, or invalid.
- **FR-007**: The system MUST expose a mechanism (API endpoint) to set a new password using a valid, non-expired, unused reset token. The request MUST include the new password and its confirmation.
- **FR-008**: The new password MUST meet minimum strength requirements (e.g., minimum length, complexity). If the password is weak or the confirmation does not match, return a validation error without invalidating the token.
- **FR-009**: After successfully updating the password, the system MUST invalidate the reset token (prevent reuse), and the user MUST be redirected to the login page.
- **FR-010**: If a subsequent reset request is made while a previous token is still valid, the system MUST invalidate the previous token and generate a new one. Only the latest token remains valid.
- **FR-011**: The system MUST NOT reveal whether a given email or phone is registered. Unregistered identifiers, inactive accounts, and successful requests all return an identical generic success message.

### Key Entities

- **PasswordResetToken**: Represents a single-use password reset authorization. Key attributes: unique token string, associated user, creation timestamp, expiration timestamp (20 min from creation), consumed flag, delivery channel (email or whatsapp). A user may have at most one valid token at any time.
- **User** (existing entity): Must have a valid email and valid phone on file for the reset to proceed. Must be in active status.
- **EmailNotification** (conceptual record of sent email): Log entry recording that a reset email was sent to a given email, at a given timestamp, with a given token reference.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A registered active user can complete the full flow (request → receive email → click link → set new password → log in) in under 5 minutes total.
- **SC-002**: The reset email is delivered to the user's inbox within 2 minutes of the request in 95% of cases.
- **SC-003**: Links expiring after 20 minutes are rejected with a clear expiration message in 100% of cases.
- **SC-004**: Already-used links are rejected with a clear "already used" message in 100% of cases.
- **SC-005**: Unregistered or inactive users receive an identical generic success message (no information leak) in 100% of cases.
- **SC-006**: Multiple reset requests invalidate previous tokens — only the latest token remains valid, verified in 100% of test scenarios.

## Assumptions

- The password reset email uses HTML format with a prominent call-to-action button containing the reset link.
- The password reset WhatsApp message uses plain text with the reset link and brief instructions.
- The reset link points to a dedicated front-end page (e.g., `/redefinir-senha?token=...`) where the user enters the new password.
- The generic success message is: "Se o email ou telefone informado estiver cadastrado, você receberá um link de redefinição de senha." (or equivalent).
- The minimum password strength follows the same policy already defined in the project (e.g., minimum 8 characters, mix of letters and numbers).
- The 20-minute expiration is counted from the moment the token is generated, not from the email send time.
- The password reset page (new password form) redirects the user to the login page upon success via the API response, not via client-side navigation logic alone.
- This API is consumed by both web and mobile clients — the reset link works in both browser and app contexts.
- The user's phone being "valid" means it passes format validation and is marked as verified in the user profile.
