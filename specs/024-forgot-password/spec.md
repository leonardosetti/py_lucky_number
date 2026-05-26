# Feature Specification: Forgot Password Link on Login Page

**Feature Branch**: `024-forgot-password`  
**Created**: 2026-05-23  
**Status**: Draft  
**Input**: User description: "crie uma especificação para retificar a página de login onde deverá ser criado um link para 'esqueci minha senha', o link redirecinará para uma página de reset de senha do usuário que será especificada posteriormente."

## User Scenarios & Testing

### User Story 1 — User requests password reset from login page (Priority: P1)

As a registered user who forgot their password, I want to see a clear link on the login page that takes me to a password reset flow, so that I can regain access to my account without needing external support.

**Why this priority**: This is the core user need — without this link, users who forget their credentials are blocked from the application, leading to frustration and support tickets. It is the minimum viable outcome.

**Independent Test**: A user visiting the login page can immediately locate and click the "Esqueci minha senha?" link and be redirected to a dedicated password reset page.

**Acceptance Scenarios**:

1. **Given** a user is on the login page, **When** they look for password recovery options, **Then** they see a clickable link labeled "Esqueci minha senha?" (or equivalent) clearly visible near the login form.
2. **Given** a user clicks the "Esqueci minha senha?" link, **When** the navigation completes, **Then** they land on a dedicated password reset page at a predictable URL path.
3. **Given** a user navigates directly to the password reset page URL, **When** the page loads, **Then** it displays content indicating it is the password recovery entry point (e.g., an email input field and instructions).

### User Story 2 — User retries login after visiting reset page (Priority: P2)

As a user who navigated to the password reset page, I want a clear way to return to the login page, so that I can try logging in again if I remember my password or after completing the reset flow.

**Why this priority**: Improves user navigation but is not critical for the core functionality to be usable.

**Independent Test**: A user on the password reset page can click a "Voltar para o login" link and return to the login page.

**Acceptance Scenarios**:

1. **Given** a user is on the password reset page, **When** they want to return to login, **Then** a visible link or button allows them to navigate back to the login page.

### Edge Cases

- **Visually impaired users**: The link must be distinguishable by more than just color (e.g., underline, icon, or sufficient contrast ratio) to meet accessibility standards.
- **Mobile viewports**: The link must remain visible and tappable on small screens without horizontal scrolling or overlapping other form elements.
- **Already logged-in users**: If a user who is already authenticated navigates directly to the reset page URL, they should be redirected away (e.g., to the dashboard or home page), as password reset is irrelevant for an active session.
- **Loading/error states**: If the destination reset page depends on an API or resource that fails to load, an appropriate error message should be displayed rather than a broken page.

## Requirements

### Functional Requirements

- **FR-001**: The login page MUST contain a clickable link labeled "Esqueci minha senha?" positioned in close proximity to the password field or login button.
- **FR-002**: The link MUST be visually distinct from regular text, using standard link affordances (underline, color contrast, pointer cursor).
- **FR-003**: Clicking the link MUST navigate the user to a dedicated password reset page at a fixed URL path (e.g., `/reset-password` or `/esqueci-minha-senha`).
- **FR-004**: The password reset page MUST exist as a navigable route and MUST state its purpose (e.g., a heading like "Redefinir sua senha").
- **FR-005**: The password reset page MUST be publicly accessible (no authentication required) since the user cannot log in.
- **FR-006**: The password reset page MUST include a link or button to return to the login page.
- **FR-007**: If an already authenticated user accesses the reset page URL, the system MUST redirect them to the default post-login destination (e.g., dashboard).
- **FR-008**: The login page link and the reset page MUST be responsive and functional on mobile, tablet, and desktop viewports.

### Out of Scope (for this specification)

The following items are explicitly out of scope and will be specified in a future document:

- The full password reset flow (email sending, token generation/validation, new password form, confirmation)
- Backend API endpoints for password reset
- Email notification templates for reset instructions
- Security mechanisms such as rate limiting, token expiry, or brute-force protection on the reset flow

### Key Entities

This feature does not introduce new data entities. The password reset page is a presentation layer element that will connect to a future reset flow.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A user on the login page can locate and click the "Esqueci minha senha?" link within 5 seconds of viewing the page.
- **SC-002**: Clicking the link navigates to the password reset page in under 2 seconds on a standard broadband connection.
- **SC-003**: The link and reset page render correctly on mobile (320px width), tablet (768px), and desktop (1280px+) viewports.
- **SC-004**: The link and reset page pass automated accessibility checks (color contrast, keyboard navigation, screen reader labels) with zero critical or serious violations.

## Assumptions

- The label "Esqueci minha senha?" is appropriate for Brazilian Portuguese users; the exact text may be adjusted during implementation.
- The link will be placed below the password field and above the login button, following common UX patterns.
- The destination URL path will be `/reset-password` (or a localized equivalent such as `/esqueci-minha-senha`), to be confirmed during implementation.
- The password reset page is a shell route with minimal content (heading + back link); the full form, validation, and backend integration are deferred to a future specification.
- An existing authentication system is in place — this feature only modifies the login page and creates a new route/page for reset.
- Mobile and desktop versions of the login page already exist; the link must be added to all variants.
