# Feature Specification: Apostador Registration Flow (MOBILE)

**Feature Branch**: `023-apostador-mobile-registration`
**Created**: 2026-05-21
**Status**: Draft
**Input**: Replicar fluxo de cadastro de apostador (spec 022) para mobile nativo.

## User Scenarios & Testing

### User Story 1 - Visitante Cria Conta pelo App (Priority: P1)

Como um visitante maior de 18 anos que baixou o app, quero criar minha conta de apostador diretamente pelo celular, preenchendo meus dados com componentes de entrada nativos, para começar a usar o sistema imediatamente no meu dispositivo móvel.

**Por que P1**: O mobile é um dos dois canais primários de acesso (Constitution VII). O cadastro precisa ser nativo e fluido.

**Teste independente**: Baixar app, tocar "Criar conta", preencher dados, escolher canal de ativação (incluindo push notification), receber código, ativar, ser logado automaticamente na tela de perfil.

**Acceptance Scenarios**:

1. **Given** visitante abre o app e toca "Criar conta", **When** preenche todos os campos obrigatórios com dados válidos e passa pela verificação nativa de segurança (SafetyNet/App Attest), **Then** a conta é criada como "pendente" e um código de ativação de 6 dígitos é gerado e enviado ao canal escolhido (email/SMS/WhatsApp/Push Notification).
2. **Given** visitante recebeu código de ativação, **When** informa o código correto, **Then** a conta é ativada, o token JWT é armazenado no cofre seguro do dispositivo (Keychain/Keystore), e o usuário é redirecionado à tela de perfil nativa.
3. **Given** visitante fecha o app durante o cadastro (interrupção), **When** reabre o app, **Then** o estado do cadastro é retomado de onde parou (desde que dentro do prazo de validade da sessão).
4. **Given** visitante recebe o código por push notification, **When** toca na notificação, **Then** o app abre diretamente na tela de ativação com o código pré-preenchido (deep link).

---

### User Story 2 - Visitante Com Dados Inválidos no Mobile (Priority: P1)

Como um visitante se cadastrando pelo celular, quero validação imediata campo a campo com feedback nativo (teclado específico, máscara de CPF, date picker de idade).

**Por que P1**: A validação nativa reduz erros de digitação e abandono.

**Teste independente**: Submeter CPF inválido, senha fraca, menor de idade — cada erro exibe mensagem nativa específica.

**Acceptance Scenarios**:

1. **Given** visitante no formulário mobile, **When** digita o CPF, **Then** o campo aplica máscara (XXX.XXX.XXX-XX) e valida os dígitos verificadores em tempo real com feedback visual.
2. **Given** visitante no campo de telefone, **When** toca no campo, **Then** o teclado numérico é exibido com formatação automática (+55 XX XXXXX-XXXX).
3. **Given** visitante no campo de data de nascimento, **When** toca, **Then** o date picker nativo é exibido com limite superior (data atual - 18 anos) para impedir seleção de menor de idade.
4. **Given** visitante digita senha, **When** a senha não atende todos os requisitos, **Then** uma lista de requisitos é exibida abaixo do campo com checkmarks dinâmicos (verde = ok, vermelho = pendente).
5. **Given** visitante no campo de confirmação de senha, **When** as senhas divergem, **Then** ícone de erro aparece no campo com mensagem "Senhas não conferem".

---

### User Story 3 - Sistema de Segurança Mobile (Priority: P1)

Como operador do sistema, quero que o cadastro mobile tenha camadas adicionais de segurança contra abuso: device fingerprinting, attestation nativa (Android SafetyNet / iOS App Attest), e biometria como segundo fator opcional.

**Por que P1**: Dispositivos móveis são mais vulneráveis a automação via emuladores e farms de devices.

**Teste independente**: Tentar cadastro em um emulador sem attestation válido — o sistema bloqueia.

**Acceptance Scenarios**:

1. **Given** visitante tenta criar conta em um emulador ou device com SafetyNet/App Attest inválido, **When** submete o formulário, **Then** o sistema rejeita a criação com erro "Dispositivo não autorizado".
2. **Given** visitante cria conta com sucesso e optou por 2FA via biometria, **When** faz login posteriormente, **Then** o app solicita Face ID / impressão digital como segundo fator.
3. **Given** visitante tenta criar múltiplas contas no mesmo dispositivo, **When** excede o limite de 3 contas por device, **Then** o sistema bloqueia com erro "Limite de contas por dispositivo atingido".

---

### User Story 4 - Usuário Gerencia Perfil no App (Priority: P2)

Como apostador recém-cadastrado pelo app, quero acessar meu perfil nativo onde posso editar meus dados (exceto CPF), alterar senha, configurar biometria e 2FA, e visualizar meu status de verificação.

**Por que P2**: O perfil é funcionalidade essencial mas não bloqueia o cadastro em si.

**Teste independente**: Após ativação, acessar perfil nativo, editar nome, alterar senha, ativar/desativar biometria.

**Acceptance Scenarios**:

1. **Given** usuário recém-ativado na tela de perfil, **When** visualiza seus dados, **Then** todos os campos são exibidos no layout nativo (iOS: grouped table view / Android: Material settings), com CPF em modo somente leitura.
2. **Given** usuário na tela de perfil, **When** altera o email, **Then** um novo código de verificação é enviado ao novo email e o email só é atualizado após confirmação.
3. **Given** usuário na seção "Segurança" do perfil, **When** ativa "Login com biometria", **Then** o sistema solicita a biometria do device (Face ID / fingerprint) e armazena o consentimento no Keychain/Keystore.
4. **Given** usuário com biometria ativa, **When** faz logout e login, **Then** após a senha, o app solicita biometria (2FA simplificado) e concede acesso se aprovado.
5. **Given** usuário na seção "Alterar senha", **When** informa senha atual + nova senha com confirmação, **Then** a senha é alterada e uma notificação push de confirmação é enviada.

---

### Edge Cases

- **Interrupção de chamada telefônica**: Se o usuário receber uma chamada durante o cadastro, o app preserva o estado do formulário ao retornar.
- **Mudança de rede (WiFi -> 4G)**: A submissão do cadastro não deve falhar durante transição de rede — usar retry automático.
- **App encerrado pelo SO**: Se o SO mata o app por falta de memória, o estado do cadastro é perdido e o usuário deve recomeçar (proteção contra dados parciais órfãos).
- **Deep link malicioso**: Links de ativação recebidos por push/email são validados contra o usuário logado — rejeitar deep links que não correspondam à sessão atual.
- **Device sem biometria**: Se o dispositivo não possui sensor biométrico, a opção de 2FA biométrico não é exibida (cair para TOTP tradicional).

## Requirements

### Functional Requirements

- **FR-001 a FR-025**: (mesmos requisitos funcionais da spec 022 — cadastro com CPF, senha forte, maioridade, ativação multicanal, CAPTCHA, anti-flood — aplicados integralmente também ao mobile)
- **FR-026**: System MUST validate device integrity via platform-native attestation (Android SafetyNet/Play Integrity, iOS App Attest) before accepting registration.
- **FR-027**: System MUST support device fingerprinting as an additional anti-abuse signal, limiting to maximum 3 accounts per device.
- **FR-028**: System MUST support activation code delivery via push notification as a fourth channel option (in addition to email, SMS, WhatsApp).
- **FR-029**: Deep link from push notification/email MUST open the app directly on the activation screen with code pre-filled where possible.
- **FR-030**: Mobile registration form MUST use native input patterns: CPF mask (XXX.XXX.XXX-XX), phone mask (+55 XX XXXXX-XXXX), native date picker with 18-year upper bound.
- **FR-031**: System MUST offer biometric authentication (Face ID / fingerprint) as a 2FA method option during registration when the device supports it.
- **FR-032**: When 2FA biometric is enabled, the device's native biometric API (Face ID / fingerprint) is used for second-factor verification on subsequent logins.
- **FR-033**: JWT token MUST be stored in platform-secure storage (iOS Keychain, Android EncryptedSharedPreferences/Keystore).
- **FR-034**: Native profile screen MUST allow editing all fields except CPF, with password change section and biometric toggle.
- **FR-035**: Mobile registration MUST handle app lifecycle events: save draft state on background, restore on foreground, timeout after 30 minutes of inactivity.
- **FR-036**: System MUST detect and prevent VPN/proxy usage during registration as an additional fraud signal (configurable).

### Key Entities

- **Apostador (User)**: (mesma entidade da spec 022)
- **Código de Ativação**: (mesma entidade da spec 022)
- **Device Fingerprint**: Identificador único e anônimo do dispositivo, gerado localmente e validado pelo servidor. Usado para anti-abuse (limite de contas por device). Não armazena dados pessoais do dispositivo (LGPD compliance).
- **Sessão de Cadastro Mobile**: Estado transitório que persiste localmente (criptografado) para permitir retomada do fluxo após interrupção do app.

## Success Criteria

### Measurable Outcomes

- **SC-001 a SC-007**: (mesmos critérios da spec 022)
- **SC-008**: Mobile registration completion rate > 85% (form start to activated account).
- **SC-009**: Device attestation blocks 100% of registration attempts from emulators or compromised devices.
- **SC-010**: Biometric 2FA setup completes in under 30 seconds (from user opt-in to enrollment confirmation).
- **SC-011**: Push notification activation code delivery in under 5 seconds.

## Assumptions

- **Dispositivos compatíveis**: Android API 26+ (8.0) e iOS 15+, conforme Constitution, com suporte a SafetyNet/Play Integrity e App Attest respectivamente.
- **Push notifications**: Serviço de push (FCM/APNs) já configurado para o app.
- **Backend compartilhado**: O mesmo backend da spec 022 atende ambos os fluxos (web e mobile) — as validações de CPF, senha, maioridade, anti-flood são centralizadas no servidor.
- **Geração de código**: A geração e validação de código de ativação é idêntica ao fluxo web (reutilizar endpoints existentes).
- **Biometria**: Dispositivos sem sensor biométrico não exibem a opção de 2FA biométrico.
- **VPN Usage**: O bloqueio de VPN durante cadastro é configurável e pode ser desativado em ambientes controlados.
