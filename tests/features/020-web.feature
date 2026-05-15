Feature: Web Frontend
  Como um usuário do sistema
  Quero uma interface web responsiva e acessível
  Para interagir com o Lucky Number

  Background:
Given que o frontend está servindo em http://localhost:3000

  Scenario: Registro de novo usuário
When o usuário acessa a página de registro
And preenche email "novo@email.com" e senha "Str0ng!Pass"
And clica em "Criar Conta" [data-testid="register-submit-button"]
Then o usuário é redirecionado para o dashboard
And o email é exibido no perfil [data-testid="profile-email"]

  Scenario: Geração de apostas com fallback para funcionalidade não implementada
Given que a API de geração retorna 503 (não implementada)
When o usuário clica em "Gerar" [data-testid="generate-submit-button"]
Then uma mensagem amigável é exibida:
"Esta funcionalidade estará disponível em breve"
And a UI não quebra (nenhum erro visível no console)

  Scenario: FIFO notification no histórico
Given que o usuário possui 200 combinações salvas
When ele gera e salva 5 novas combinações
Then uma notificação é exibida:
"Limite de 200 combinações atingido. As 5 mais antigas foram removidas."
[data-testid="fifo-notification"]

  Scenario: Responsividade em viewport 375px (iPhone SE)
Given que o viewport é 375x667
When a página de geração carrega
Then a navegação usa bottom tabs [data-testid="bottom-nav"]
And todos os touch targets têm no mínimo 48x48px
And o layout não tem overflow horizontal

  Scenario: data-testid em todos os elementos interativos
Given que a página de login está renderizada
Then o email input tem [data-testid="email-input"]
And o password input tem [data-testid="password-input"]
And o botão de submit tem [data-testid="login-submit-button"]
And a mensagem de erro tem [data-testid="error-login"]

  Scenario: WCAG 2.2 AA sem violações
Given que todas as páginas foram carregadas
When o axe-core audit é executado
Then zero violações WCAG 2.2 AA são reportadas

  Scenario: Session timeout redireciona para login
Given que o JWT do usuário expirou
When ele tenta acessar o dashboard
Then ele é redirecionado para a página de login
And um toast é exibido: "Sessão expirada. Faça login novamente."

  Scenario: Empty state no histórico
Given que o usuário não possui combinações salvas
When ele acessa a página de histórico
Then uma mensagem é exibida:
"Você ainda não gerou nenhuma combinação. Que tal começar?"
[data-testid="empty-state-history"]
And um CTA "Gerar Agora" está presente [data-testid="empty-state-cta"]
