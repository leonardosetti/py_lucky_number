Feature: Promessas de Aposta
  Como um usuário do sistema
  Quero criar, gerenciar e compartilhar promessas de aposta
  Para planejar meus gastos com loterias

  Background:
Given que o usuário "maria@email.com" está autenticado
And que o usuário possui 3 combinações salvas

  Scenario: Criar promessa com título e prioridade
Given que o usuário seleciona 2 combinações
When ele clica em "Criar Promessa"
And preenche o título "Aposta Final de Semana"
And seleciona prioridade "Alta"
Then o sistema persiste a promessa com snapshot das combinações
And o valor total da promessa é calculado corretamente

  Scenario: FIFO ao atingir 50 promessas
Given que o usuário possui 50 promessas salvas
And a mais antiga não é favorita
When ele cria uma nova promessa
Then a promessa mais antiga não favorita é removida
And o sistema exibe notificação "Limite de 50 promessas atingido"

  Scenario: Compartilhar promessa via WhatsApp
Given que o usuário possui uma promessa salva
When ele clica em "Compartilhar via WhatsApp"
Then um link wa.me é gerado com as combinações em texto puro
And o link expira em 7 dias

  Scenario: Excluir promessa com confirmação
Given que o usuário possui uma promessa
When ele clica em "Excluir"
Then um diálogo de confirmação é exibido
When ele confirma a exclusão
Then a promessa é removida

  Scenario: Erro ao criar promessa sem combinações
Given que o usuário não selecionou nenhuma combinação
When ele tenta criar uma promessa
Then o sistema exibe erro "Selecione ao menos uma combinação"

  Scenario: Rejeitar duplicata de promessa
Given que o usuário já possui uma promessa com as mesmas combinações
When ele tenta criar outra idêntica
Then o sistema impede a criação com erro "Promessa duplicada"
