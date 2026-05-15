Feature: Export & Share
  Como um usuário autenticado
  Quero exportar e compartilhar minhas combinações
  Para usar fora do sistema

  Background:
Given que o usuário "maria@email.com" está autenticado
And que o usuário possui 10 combinações salvas

  Scenario: Exportar CSV
When o usuário acessa GET /api/v1/export/csv
Then o response é um arquivo CSV baixável
And contém apenas as combinações do próprio usuário
And o CSV tem os cabeçalhos: jogo, dezenas, data

  Scenario: Exportar JSON
When o usuário acessa GET /api/v1/export/json
Then o response é um JSON array baixável
And contém as 10 combinações do usuário

  Scenario: Exportar PDF
When o usuário acessa GET /api/v1/export/pdf
Then o response é um PDF baixável
And o PDF contém as combinações formatadas

  Scenario: Compartilhar entre usuários
Given que o usuário "joao@email.com" existe
When o usuário compartilha uma combinação com joao@email.com
Then joao@email.com recebe uma notificação com a combinação

  Scenario: Link expira após 7 dias
Given que um link de compartilhamento foi gerado
When 8 dias se passam
Then o link não é mais válido
And o acesso retorna 404

  Scenario: Usuário A não exporta dados do usuário B
Given que "joao@email.com" está autenticado
When ele tenta exportar as combinações de "maria@email.com"
Then o sistema retorna apenas as combinações de joao

  Scenario: Sem combinações para exportar
Given que o usuário não possui combinações salvas
When ele tenta exportar CSV
Then o sistema retorna CSV vazio (apenas cabeçalhos)
Or retorna erro amigável "Nenhuma combinação para exportar"
