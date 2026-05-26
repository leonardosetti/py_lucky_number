# Feature Specification: Password Recovery Page

**Feature Branch**: `025-password-recovery`  
**Created**: 2026-05-23  
**Status**: Draft  
**Input**: User description: "crie uma especificação para uma página de recuperação de senha do usuário, esta página deverá conter apenas o campo para identificação do usuário ou por email ou por telefone (use mascara no padrão BR (DDD)99999-9999) e a opção enviar por email ou enviar por whatsapp, esta página deverá usar a API de reset password a ser especificada"

## User Scenarios & Testing

### User Story 1 — User requests password recovery via email (Priority: P1)

As a registered user who forgot my password, I want to enter my email and receive a password reset link by email, so that I can reset my password and regain access to my account.

**Why this priority**: This is the primary recovery path — email is the most common identification method and the default delivery channel for reset links.

**Independent Test**: A user on the password recovery page can enter a valid registered email, select "enviar por email", submit the form, and receive a success confirmation message indicating the reset link was sent to their email.

**Acceptance Scenarios**:

1. **Given** a user is on the password recovery page, **When** they enter a valid registered email in the identification field and select "enviar por email", **Then** the system accepts the input and displays a success message confirming the reset link was sent.
2. **Given** a user enters an unregistered email, **When** they submit the form, **Then** the system displays a generic error message (without revealing whether the email is registered, for security).
3. **Given** a user submits a recovery request via email, **When** the request succeeds, **Then** they see a message instructing them to check their email inbox for the reset link and providing a way to return to the login page.

### User Story 2 — User requests password recovery via WhatsApp (Priority: P1)

As a registered user who forgot my password and prefers WhatsApp, I want to enter my phone number and receive the password reset link by WhatsApp, so that I can reset my password conveniently.

**Why this priority**: WhatsApp is explicitly required by the feature description and provides an alternative channel for users who may not have email access.

**Independent Test**: A user on the password recovery page can enter a valid registered BR phone number (with automatic mask), select "enviar por WhatsApp", submit the form, and receive a success confirmation message.

**Acceptance Scenarios**:

1. **Given** a user is on the password recovery page, **When** they enter a valid registered phone in the identification field (auto-formatted as (DD)99999-9999) and select "enviar por WhatsApp", **Then** the system accepts the input and displays a success message.
2. **Given** a user enters a phone in the identification field, **When** the field loses focus or they pause typing, **Then** the number is automatically formatted with the BR mask (DD)99999-9999.
3. **Given** a user submits a recovery request via WhatsApp, **When** the request succeeds, **Then** they see a message instructing them to check their WhatsApp messages.

### User Story 3 — User corrects mismatched identification and delivery channel (Priority: P2)

As a user, if I select a delivery channel that does not match my identification method (e.g., entered phone but selected "enviar por email"), I want a clear validation error so that I can correct my choice before submitting.

**Why this priority**: Prevents failed submissions and user confusion. Important for usability but not critical for the basic flow.

**Independent Test**: A user enters a phone number, selects "enviar por email", and is shown a clear validation message explaining the mismatch before submission.

**Acceptance Scenarios**:

1. **Given** a user enters a phone number and selects "enviar por email", **When** they attempt to submit, **Then** the system shows a validation error: "Para envio por email, informe um email válido" (or equivalent).
2. **Given** a user enters an email and selects "enviar por WhatsApp", **When** they attempt to submit, **Then** the system shows a validation error: "Para envio por WhatsApp, informe um telefone válido" (or equivalent).
3. **Given** a user corrects the mismatch after seeing a validation error, **When** they resubmit with valid matching data, **Then** the submission proceeds successfully.

### Edge Cases

- **Unregistered identifier**: If the email or phone does not match any registered account, the system must return a generic success message (to prevent user enumeration attacks) — never reveal whether the identifier is registered.
- **Invalid format**: If the email format is invalid or the phone does not match the BR pattern, show a format-specific validation error before submission.
- **API unavailable**: If the backend API (to be specified) is unreachable, display a friendly error message and a "tentar novamente" button. Do not leave the user on a broken page.
- **Rate limiting**: If the user submits too many requests in a short period, display a rate-limit message with guidance on when to try again.
- **Previously submitted**: If the user successfully submitted and then revisits the page, the page should reset to its initial state (not show stale success/error messages).

## Requirements

### Functional Requirements

- **FR-001**: The password recovery page MUST contain a single identification input field that accepts either a valid email address or a Brazilian phone number.
- **FR-002**: When the user types a phone number, the field MUST auto-format to the BR mask pattern (DD)99999-9999 as the user types or on field blur.
- **FR-003**: The page MUST present two mutually exclusive delivery channel options: "Enviar por email" and "Enviar por WhatsApp", selectable via radio buttons or equivalent UI control.
- **FR-004**: The system MUST validate that the selected delivery channel matches the identification type: email must be selected when an email is entered, WhatsApp must be selected when a phone is entered. If mismatched, show a clear validation error and block submission.
- **FR-005**: A submit button (labeled "Enviar link de recuperação" or equivalent) MUST trigger the recovery request.
- **FR-006**: Upon successful submission, the page MUST display a success message confirming that a reset link has been sent via the chosen channel, along with instructions.
- **FR-007**: If the email or phone format is invalid, the system MUST display a format-specific error message before allowing submission.
- **FR-008**: The page MUST include a link to return to the login page.
- **FR-009**: The page MUST be publicly accessible (no authentication required), as the user cannot log in.
- **FR-010**: The page MUST be responsive and fully functional on mobile, tablet, and desktop viewports.
- **FR-011**: If an already authenticated user accesses this page URL, they MUST be redirected to their dashboard or home page.

### Out of Scope (for this specification)

- The backend API endpoints for password reset (specified in spec 026-password-reset-api).
- The actual sending of reset links via email or WhatsApp (handled by the spec 026 API).
- The new password form (separate page/flow).
- SMS as a delivery channel (only email and WhatsApp are in scope).

### Key Entities

This feature does not introduce new data entities. It defines a front-end page that will interface with a future password reset API.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A user can complete the identification + delivery channel selection and submit the form in under 30 seconds.
- **SC-002**: The phone field auto-formats to (DD)99999-9999 within 500ms of the user finishing typing or on field blur.
- **SC-003**: Validation errors (format mismatch, invalid input) appear within 1 second of triggering the condition.
- **SC-004**: The page renders correctly on mobile (320px), tablet (768px), and desktop (1280px+).
- **SC-005**: The page passes automated accessibility checks with zero critical or serious violations (keyboard navigation, screen reader labels, color contrast).
- **SC-006**: Users who enter an unregistered identifier receive a generic success message (no enumeration leak) in 100% of cases.

## Assumptions

- The identification field auto-detects whether the input is an email or phone based on format (presence of `@` = email, digits only = phone).
- The delivery channel defaults to "Enviar por email" when the page loads.
- The BR phone mask follows the pattern (DD)99999-9999, accommodating both 8-digit and 9-digit phone numbers (landline and mobile).
- The password reset API (spec 026) will accept at minimum: user identifier (email or phone), delivery channel (email or WhatsApp), and will return a success acknowledgment.
- Error messages from the API follow the same generic-response pattern to prevent user enumeration.
- The page URL path is `/recuperar-senha` or similar, consistent with the link defined in spec 024-forgot-password.
