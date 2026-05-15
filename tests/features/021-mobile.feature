Feature: Mobile App
  Como um usuário mobile
  Quero usar o Lucky Number no celular com biometria e offline
  Para acessar minhas combinações em qualquer lugar

  Background:
Given que o app está instalado no dispositivo

  Scenario: Login com biometria
Given que o usuário já fez login uma vez e ativou biometria
When ele abre o app
Then o Face ID / fingerprint é solicitado
When a biometria é bem-sucedida
Then o usuário acessa o Home sem digitar credenciais

  Scenario: Geração offline bloqueada
Given que o dispositivo está offline
When o usuário tenta gerar combinações
Then uma mensagem é exibida:
"Geração requer conexão com a internet"
And o botão "Gerar" permanece desabilitado

  Scenario: Histórico visível offline (cache)
Given que o usuário possui combinações em cache local (SQLite)
When o dispositivo está offline
When ele acessa o histórico
Then as combinações em cache são exibidas
And um banner é mostrado: "Você está offline"

  Scenario: Swipe para excluir
Given que o usuário está no histórico
When ele desliza uma combinação para a esquerda
Then um botão "Excluir" é revelado
When ele toca em "Excluir"
Then a combinação é removida

  Scenario: Push notification para novo sorteio
Given que as permissões de push estão ativadas
When um novo sorteio da Mega-Sena é publicado
Then o usuário recebe uma notificação:
"Mega-Sena: novo sorteio disponível!"
When ele toca na notificação
Then o app abre na tela de geração com Mega-Sena pré-selecionada

  Scenario: Deep link de promessa compartilhada
Given que um link luckynumber://promise/abc123 foi gerado
When o usuário toca no link
Then o app abre na tela de detalhes da promessa
And exibe as combinações do snapshot

  Scenario: Tema escuro segue configuração do sistema
Given que o dispositivo está configurado com tema escuro
When o app é aberto
Then o tema escuro é aplicado automaticamente
And todos os componentes respeitam as cores do tema

  Scenario: Fallback de biometria para senha
Given que a biometria falhou 3 vezes consecutivas
When o usuário tenta autenticar
Then o sistema solicita a senha da conta
And a biometria fica bloqueada para a sessão atual
