Feature: Database Architecture
  Como um desenvolvedor
  Quero garantir que o banco de dados funcione conforme especificado
  Para manter a integridade, performance e segurança dos dados

  Background:
Given que o banco PostgreSQL está configurado com o schema da spec 004

  Scenario: 4 ambientes isolados
Given que a variável DATABASE_URL aponta para o ambiente de desenvolvimento
When a aplicação inicia
Then ela conecta-se exclusivamente ao banco de desenvolvimento
And operações de escrita não afetam produção ou testes

  Scenario: Migrations com rollback automático
Given que uma migration com erro é aplicada
When a migration falha (violação de constraint)
Then o rollback é executado automaticamente
And o erro é registrado em migrations_history

  Scenario: Unique hash em sorteios_historicos
Given que existe um registro com hash "abc123" para Mega-Sena
When uma tentativa de inserir outro registro com mesmo hash é feita
Then o banco rejeita com erro de unique constraint

  Scenario: Soft delete de usuário
Given que o usuário "maria@email.com" é marcado como inativo
When o sistema consulta a listagem ativa de usuários
Then "maria@email.com" não aparece nos resultados
And o registro permanece no banco com deleted_at preenchido

  Scenario: Limite de 200 combinações por usuário
Given que o usuário possui 200 combinações salvas
When ele tenta salvar uma nova combinação
Then a aplicação rejeita com erro "Limite de 200 combinações atingido"
Or a mais antiga não favorita é removida para abrir espaço

  Scenario: BRIN index em usage_events
Given que a tabela usage_events possui 1 milhão de registros
When uma consulta por período é executada
Then o BRIN index em created_at é utilizado (verificar via EXPLAIN)

  Scenario: pg_stat_statements coletando snapshots
Given que o Celery Beat está configurado
When o coletor de performance executa a cada 15 minutos
Then um snapshot é inserido em database_performance_snapshots
