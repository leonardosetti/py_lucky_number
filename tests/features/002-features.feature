Feature: Feature Toggles
  Como um administrador
  Quero ativar e desativar funcionalidades do sistema
  Para controlar a disponibilidade de features em produção

  Background:
Given que o admin "admin@sistema.com" está autenticado com role Admin

  Scenario: Listar todas as features
Given que existem features cadastradas
When o admin acessa o painel de features
Then a lista exibe slug, nome, descrição, status e data de criação
And a lista contém pelo menos 4 features: "geracao-apostas", "promessas", "export", "admin"

  Scenario: Alternar status de feature
Given que a feature "geracao-apostas" está ativa
When o admin alterna o toggle para "inativa"
Then o status da feature é alterado para "inativa"
And o cache é invalidado
And um registro é criado em feature_toggle_audit

  Scenario: Usuário não-admin não acessa painel
Given que o usuário "maria@email.com" está autenticado com role Apostador
When ele tenta acessar GET /api/v1/admin/features
Then o sistema retorna 403 Forbidden

  Scenario: Feature desativada bloqueia acesso
Given que a feature "geracao-apostas" está inativa
When um usuário tenta acessar POST /api/v1/gerar-apostas
Then o sistema retorna 404 com mensagem "Feature indisponível"

  Scenario: Toggle concorrente com optimistic locking
Given que dois admins acessam a mesma feature simultaneamente
When ambos tentam alterar o toggle
Then apenas o primeiro commit é aceito
And o segundo recebe erro de concorrência (version conflict)
