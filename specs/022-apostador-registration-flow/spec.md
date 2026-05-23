# Feature Specification: Apostador Registration Flow (WEB)

**Feature Branch**: `022-apostador-registration-flow`
**Created**: 2026-05-21
**Status**: Draft
**Input**: Fluxo de criação do usuário do tipo apostador via web.

## User Scenarios & Testing

### User Story 1 - Visitante Cria Conta de Apostador (Priority: P1)

Como um visitante maior de 18 anos interessado em gerar combinações, quero criar minha conta de apostador com dados reais (CPF, nome, data de nascimento, telefone, email e senha forte), validar minha identidade pelo canal que preferir (email, SMS ou WhatsApp) e ativar minha conta para começar a usar o sistema imediatamente.

**Por que P1**: Sem cadastro, o usuário não pode salvar combinações, criar promessas ou acessar funcionalidades persistentes. Este é o primeiro passo da jornada do apostador.

**Teste independente**: Preencher formulário com dados válidos, submeter, receber código de ativação, informar código, ser automaticamente logado e redirecionado ao perfil. Todo o fluxo é testável sem depender de outras features.

**Acceptance Scenarios**:

1. **Given** visitante na página de cadastro, **When** preenche todos os campos obrigatórios com dados válidos, passa no CAPTCHA e submete, **Then** a conta é criada em estado "pendente" e um código de ativação de 6 dígitos é gerado e enviado ao canal escolhido (email/SMS/WhatsApp).
2. **Given** visitante submeteu cadastro com sucesso, **When** informa o código de ativação correto dentro do prazo de validade, **Then** a conta é ativada, o usuário é autenticado automaticamente e redirecionado à página de perfil.
3. **Given** visitante submeteu cadastro, **When** informa código de ativação incorreto, **Then** exibe mensagem de erro e permite nova tentativa (limite de 5 tentativas antes de bloquear o código).
4. **Given** visitante recebeu o código de ativação, **When** o código expira (24h sem ativação), **Then** a conta pendente é removida e o usuário deve recomeçar o cadastro.

---

### User Story 2 - Visitante com Dados Inválidos Recebe Feedback (Priority: P1)

Como um visitante tentando se cadastrar, quero receber validação imediata e clara de cada campo para corrigir erros antes de submeter.

**Por que P1**: A experiência de cadastro determina a taxa de conversão. Erros silenciosos ou mensagens genéricas afastam usuários.

**Teste independente**: Submeter formulário com CPF inválido, senha fraca, menor de idade, nome vazio — cada caso produz erro específico no campo correspondente.

**Acceptance Scenarios**:

1. **Given** visitante no formulário de cadastro, **When** informa um CPF com formato ou dígitos verificadores inválidos, **Then** o campo CPF exibe erro "CPF inválido" antes da submissão.
2. **Given** visitante no formulário, **When** informa data de nascimento que indica idade inferior a 18 anos, **Then** exibe erro "Você precisa ter 18 anos ou mais para se cadastrar".
3. **Given** visitante no formulário, **When** informa senha sem todos os requisitos (8+ chars, maiúscula, minúscula, número, especial), **Then** exibe erro descritivo no campo senha listando os requisitos faltantes.
4. **Given** visitante no formulário, **When** informa senha e confirmação divergentes, **Then** exibe erro "Senhas não conferem" no campo de confirmação.

---

### User Story 3 - Sistema Previne Abuso de Cadastro (Priority: P1)

Como operador do sistema, quero que o cadastro tenha proteções contra criação automatizada massiva de contas, garantindo que apenas humanos reais possam se registrar.

**Por que P1**: Sem proteção antifraude, o sistema fica vulnerável a criação de contas em massa para ataques, scraping ou manipulação.

**Teste independente**: Tentar criar múltiplas contas consecutivas pelo mesmo IP sem aguardar o delay configurado — o sistema bloqueia as tentativas sucessivas.

**Acceptance Scenarios**:

1. **Given** um IP que acabou de criar uma conta, **When** tenta criar outra conta em menos de 30 segundos, **Then** o sistema rejeita com erro "Aguarde antes de criar outra conta" e retorna o tempo restante.
2. **Given** um visitante no formulário de cadastro, **When** não completa o CAPTCHA, **Then** a submissão é bloqueada.
3. **Given** múltiplas tentativas de cadastro com o mesmo email ou CPF em intervalo curto, distintas por IP, **When** o sistema detecta o padrão, **Then** aplica rate limiting progressivo (delay maior a cada tentativa) e registra alerta de segurança.
4. **Given** um email ou CPF já cadastrado no sistema, **When** visitante tenta cadastrar novamente, **Then** exibe erro "Email já cadastrado" ou "CPF já cadastrado".

---

### User Story 4 - Usuário Ativa 2FA Durante Cadastro (Priority: P2)

Como um apostador preocupado com segurança, quero ativar a autenticação de dois fatores (2FA) opcionalmente durante o cadastro, para proteger minha conta contra acessos não autorizados.

**Por que P2**: 2FA é importante para segurança mas não bloqueia a criação da conta — pode ser configurado após o cadastro também.

**Teste independente**: Marcar "ativar 2FA" no cadastro, finalizar fluxo, fazer logout, tentar login — o sistema exige o segundo fator antes de conceder acesso.

**Acceptance Scenarios**:

1. **Given** visitante no cadastro, **When** marca a opção "Ativar verificação em duas etapas (2FA)", **Then** o sistema exibe as instruções de configuração (aplicativo autenticador) e um QR Code para escanear.
2. **Given** visitante ativou 2FA durante o cadastro, **When** a conta é ativada e o login é realizado automaticamente, **Then** o segundo fator não é exigido (a sessão atual já é confiável), mas será exigido em próximos logins.
3. **Given** usuário com 2FA ativo, **When** tenta fazer login, **Then** após senha correta, o sistema solicita o código TOTP de 6 dígitos antes de conceder acesso completo.

---

### User Story 5 - Usuário Gerencia Perfil Após Ativação (Priority: P2)

Como um apostador recém-cadastrado, quero acessar minha página de perfil onde posso visualizar e editar meus dados (exceto CPF) e alterar minha senha, mantendo meu cadastro sempre atualizado.

**Por que P2**: O perfil é importante para manutenção cadastral mas não bloqueia o uso do sistema.

**Teste independente**: Após ativação e login automático, acessar perfil, editar nome, telefone e email, confirmar alterações.

**Acceptance Scenarios**:

1. **Given** usuário autenticado na página de perfil, **When** visualiza seus dados, **Then** todos os campos são exibidos com Nome, Email, Telefone, Data de nascimento editáveis, e CPF exibido apenas para leitura.
2. **Given** usuário na página de perfil, **When** altera o nome e salva, **Then** as alterações são persistidas imediatamente com mensagem de sucesso.
3. **Given** usuário na página de perfil, **When** altera o email, **Then** o sistema pode exigir confirmação do novo email (reenvio de código de ativação para o novo endereço).
4. **Given** usuário na página de perfil, **When** acessa a seção "Alterar senha", informa senha atual + nova senha + confirmação, **Then** a senha é alterada e o usuário é notificado.
5. **Given** usuário na página de perfil, **When** tenta editar o CPF, **Then** o campo não é editável (exibido como apenas leitura), com mensagem "CPF não pode ser alterado".

---

### Edge Cases

- **CPF já cadastrado por outro usuário**: Bloquear duplicidade com mensagem clara "CPF já possui cadastro. Esqueceu sua senha?"
- **Email já cadastrado**: Bloquear duplicidade com opção de recuperação de senha.
- **Código de ativação expirado**: Remover conta pendente, permitir novo cadastro com mesmo email/CPF.
- **Mudança de canal após envio do código**: Se o usuário escolheu email mas depois quer receber por SMS — deve solicitar novo código (o antigo é invalidado).
- **Timeouts de entrega**: Se SMS/WhatsApp falhar, o sistema tenta automaticamente o próximo canal disponível ou notifica o usuário para escolher outro método.
- **Sessão perdida durante ativação**: Se o usuário fechar o navegador antes de ativar, deve poder retornar com o código via página de ativação (informando email/CPF + código recebido).
- **Número de telefone já em uso**: Verificar duplicidade de telefone (comunicação sensível — pode indicar múltiplas contas).
- **Tentativas excessivas de ativação**: Após 5 tentativas com código errado, bloquear o código e gerar um novo (enviado ao canal escolhido).

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a web registration form with mandatory fields: Nome (full name), CPF (Brazilian individual taxpayer ID), Data de Nascimento (date of birth), Telefone (mobile phone), Email, Senha (password), and Confirmação de Senha (password confirmation).
- **FR-002**: System MUST validate CPF using the official Brazilian CPF algorithm (including both check digits), both client-side and server-side.
- **FR-003**: System MUST validate Nome as non-empty, containing only letters, spaces, and common name characters (accents, hyphens, apostrophes).
- **FR-004**: System MUST validate Data de Nascimento as a valid date and MUST reject registration for users under 18 years of age.
- **FR-005**: System MUST enforce strong password policy: minimum 8 characters, at least one uppercase letter, one lowercase letter, one digit, and one special character.
- **FR-006**: System MUST require password confirmation field that MUST match the password field exactly.
- **FR-007**: System MUST present a CAPTCHA challenge before accepting form submission.
- **FR-008**: System MUST enforce a minimum delay between consecutive registration attempts from the same source (IP), with clear feedback showing remaining wait time.
- **FR-009**: System MUST implement progressive rate limiting: escalating delays for repeated registration attempts from the same IP or using the same email/CPF.
- **FR-010**: System MUST detect and block duplicate email and duplicate CPF at registration time with specific error messages.
- **FR-011**: Upon successful form submission, system MUST create the account in "pending activation" status and generate a numeric activation code (6 digits).
- **FR-012**: System MUST present the user with a choice of activation channel at registration time: Email, SMS, or WhatsApp.
- **FR-013**: System MUST deliver the activation code exclusively via the channel chosen by the user.
- **FR-014**: Activation code MUST have a configurable expiration (default 24 hours). Expired codes invalidate the pending account.
- **FR-015**: User MUST be able to enter the activation code on a dedicated activation page/step after registration.
- **FR-016**: System MUST allow up to 5 incorrect activation code attempts before invalidating the code and requiring a new one.
- **FR-017**: User MUST be able to request a new activation code (via same or different channel), which invalidates the previous code.
- **FR-018**: Upon successful activation, system MUST automatically authenticate the user and redirect to the user profile page.
- **FR-019**: System MUST offer optional 2FA (TOTP-based) setup during registration, with QR code for authenticator app configuration.
- **FR-020**: When 2FA is enabled during registration, the current session (post-activation) is trusted and does not require 2FA; subsequent logins will require the TOTP code.
- **FR-021**: System MUST provide a user profile page accessible after login where: Nome, Email, Telefone, and Data de Nascimento are editable, but CPF is permanently read-only.
- **FR-022**: Profile page MUST include a password change section requiring current password, new password with same complexity rules, and confirmation.
- **FR-023**: Changing email on profile page SHOULD trigger email confirmation (activation cycle) before the new email is persisted.
- **FR-024**: System MUST NOT expose activation codes in logs, API responses, or any non-secure channel (CWE-200 compliance).
- **FR-025**: Web session after auto-login MUST follow existing session policies (JWT in HttpOnly cookie, configurable timeout).

### Key Entities

- **Apostador (User)**: Pessoa física que utiliza o sistema para gerar combinações. Dados cadastrais: nome, CPF (imutável), data de nascimento, telefone móvel, email, senha (hash bcrypt), status da conta (pendente/ativo/desativado), preferência de canal de ativação. Representa a identidade central do usuário no sistema.
- **Código de Ativação**: Token numérico de 6 dígitos, gerado no momento do cadastro, vinculado a um usuário específico e a um canal de entrega (email/SMS/WhatsApp). Possui data de expiração (24h) e contador de tentativas (máx. 5). É invalidado após uso, expiração ou solicitação de novo código.
- **Sessão de Cadastro**: Estado transitório que acompanha o fluxo de registro do início até a ativação. Mantém dados parciais, escolha de canal e código gerado. É limpa após conclusão ou expiração.

## Success Criteria

### Measurable Outcomes

- **SC-001**: User completes full registration flow (form fill -> activation -> profile) in under 5 minutes on first attempt.
- **SC-002**: At least 90% of users who start registration complete the full flow (form-to-activated conversion rate).
- **SC-003**: Invalid form submissions show field-level error messages within 1 second of attempted submission.
- **SC-004**: Activation code delivery reaches the user's chosen channel in under 60 seconds for email, under 30 seconds for SMS, under 10 seconds for WhatsApp.
- **SC-005**: Rate limiting blocks 100% of automated mass-registration attempts (defined as >5 attempts/IP/minute).
- **SC-006**: User account with pending activation that exceeds 24h is automatically cleaned up with zero orphaned data.
- **SC-007**: 100% of profile data changes are persisted and reflected on next page load.

## Assumptions

- **Web exclusivo**: Este fluxo de cadastro é para a interface web apenas. O mobile pode ter fluxo próprio posterior (spec 023).
- **Integração com serviços externos**: Entrega de SMS e WhatsApp depende de serviços terceiros (Twilio, WhatsApp Business API, ou similares) que serão integrados durante implementação.
- **CAPTCHA**: Serviço de CAPTCHA externo (reCAPTCHA, hCaptcha ou similar) será integrado para validação anti-automação.
- **TOTP para 2FA**: Autenticação de dois fatores usará padrão TOTP (Time-based One-Time Password), compatível com Google Authenticator, Authy e similares.
- **Envio de email transacional**: Serviço de email transacional (SMTP ou API) disponível para entrega de códigos de ativação e confirmações.
- **JWT existente**: O sistema de autenticação JWT já implementado (HttpOnly cookies, refresh tokens) será reutilizado.
- **LGPD**: Dados pessoais (CPF, telefone, data de nascimento) são armazenados com proteção adequada e política de retenção conforme legislação brasileira.
- **CPF único**: O CPF funciona como segundo identificador único (além do email) para prevenir duplicidade de cadastro.
