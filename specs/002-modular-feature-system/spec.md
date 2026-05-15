# Feature Specification: Modular Feature System

**Feature Branch**: `002-modular-feature-system`
**Created**: 2026-05-11
**Status**: Draft
**Input**: User description: "Inclua uma especificação para quebrar o projeto em features modulares de mode que cada feature possa ser 'enabled' ou 'disabled'. Este mecanismo para ativar ou desativar uma feature será possível através de uma feature de management que será de acesso exclusivo pela role Admin do sistema; Neste momento estabeleça a metodologia para que toda feature seja independente possa sofrer modificações sem afetar outras features, sua validação deve ser independente previnindo falhas de testes de regressão."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin Visualiza e Gerencia Features (Priority: P1)

Como um administrador do sistema, quero acessar um painel de controle onde possa visualizar todas as features modulares cadastradas, seu status (ativada/desativada) e alterná-las individualmente, para controlar quais funcionalidades estão disponíveis para os usuários sem precisar alterar código ou reiniciar o servidor.

**Why this priority**: Esta é a funcionalidade core do sistema de features — sem a capacidade de gerenciar (listar e alternar) o estado das features, o mecanismo de toggle não tem utilidade prática.

**Independent Test**: Pode ser testado acessando o painel admin, visualizando a lista de features, alternando o estado de uma feature de "ativada" para "desativada" e confirmando que a mudança de status é refletida imediatamente na resposta da API.

**Acceptance Scenarios**:

1. **Given** que o admin está autenticado no sistema, **When** ele acessa o endpoint de listagem de features, **Then** o sistema retorna todas as features cadastradas com seus respectivos nomes, descrições e status (ativo/inativo).
2. **Given** que o admin visualiza a lista de features, **When** ele alterna o status de uma feature específica, **Then** o sistema persiste a alteração no banco de dados e retorna o novo status da feature.
3. **Given** que um usuário não-admin tenta acessar o endpoint de gerenciamento de features, **When** ele faz a requisição, **Then** o sistema retorna erro de permissão negada (403).

---

### User Story 2 - Sistema Valida Features Ativas por Requisição (Priority: P1)

Como o sistema, quero validar automaticamente se uma feature está ativa antes de processar qualquer requisição a ela, para que funcionalidades desativadas não sejam executadas acidentalmente, garantindo consistência entre o toggle e o comportamento observável.

**Why this priority**: Sem esta validação automática, a desativação de uma feature seria inócua — o toggle não teria efeito real no sistema.

**Independent Test**: Pode ser testado desativando uma feature via painel admin e, em seguida, tentando acessar um endpoint pertencente àquela feature como usuário comum — a requisição deve ser rejeitada.

**Acceptance Scenarios**:

1. **Given** que a feature "geracao-apostas" está desativada, **When** um usuário tenta acessar o endpoint `/api/v1/gerar-apostas`, **Then** o sistema retorna erro 404 ou 503 com a mensagem "Feature indisponível".
2. **Given** que a feature "geracao-apostas" está ativada novamente, **When** um usuário tenta acessar o endpoint `/api/v1/gerar-apostas`, **Then** o sistema processa a requisição normalmente.

---

### User Story 3 - Desenvolvedor Cria Nova Feature Modular (Priority: P2)

Como um desenvolvedor do sistema, quero uma metodologia clara e um template para criar novas features modulares, de modo que cada feature seja autocontida em seu próprio diretório com seus próprios modelos, serviços, rotas e testes, garantindo isolamento completo e eliminando risco de regressão em outras features.

**Why this priority**: A adoção consistente do padrão modular depende de uma metodologia bem definida. Sem ela, cada desenvolvedor pode interpretar a modularidade de forma diferente, comprometendo o isolamento.

**Independent Test**: Pode ser testado criando uma nova feature seguindo o template, implementando seus testes de forma isolada, e executando apenas os testes daquela feature — nenhum teste de outra feature deve ser afetado ou precisar ser executado.

**Acceptance Scenarios**:

1. **Given** a metodologia de features modulares definida, **When** um desenvolvedor cria uma nova feature seguindo o template, **Then** a feature possui seu próprio diretório com modelos, serviços, rotas e testes sem importar módulos de outras features.
2. **Given** uma nova feature implementada, **When** o desenvolvedor executa os testes isolados da feature, **Then** nenhum teste de features existentes falha (zero regressão).
3. **Given** uma feature modular, **When** ela é cadastrada no registro central de features, **Then** ela automaticamente aparece no painel admin com toggle on/off.

---

### User Story 4 - Feature Flag Persistida no Banco de Dados (Priority: P2)

Como o sistema, quero que o estado de cada feature (ativada/desativada) seja persistido em uma tabela dedicada no banco de dados PostgreSQL, garantindo que o estado sobreviva a reinicializações do servidor e seja consistente entre múltiplas instâncias.

**Why this priority**: Sem persistência, os toggles seriam perdidos a cada restart, tornando o mecanismo inútil em produção com múltiplas instâncias.

**Independent Test**: Pode ser testado desativando uma feature, reiniciando o servidor, e confirmando que a feature permanece desativada após o restart.

**Acceptance Scenarios**:

1. **Given** que uma feature foi desativada via painel admin, **When** o servidor é reiniciado, **Then** a feature permanece desativada.
2. **Given** múltiplas instâncias do servidor, **When** o admin altera o status de uma feature, **Then** todas as instâncias refletem a alteração na próxima requisição.

---

### Edge Cases

- **Feature não cadastrada**: Se uma feature não estiver cadastrada na tabela de features, o sistema deve tratá-la como desativada por padrão, nunca como ativa.
- **Toggle concorrente**: Se dois admins tentarem alterar o status da mesma feature simultaneamente, o sistema deve garantir consistência via locking otimista (versionamento da linha).
- **Remoção de feature**: Quando uma feature é removida do código, seu registro na tabela de features deve ser removido para evitar acúmulo de registros órfãos. A remoção deve ser feita via script de migração.
- **Feature com dependências**: Caso uma feature dependa de outra para funcionar, a desativação da feature dependente deve ser bloqueada ou alertada no painel admin.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE manter um registro central de features com os campos: `id` (UUID), `slug` (identificador único textual), `nome` (display name), `descricao`, `ativa` (boolean), `version` (INTEGER, optimistic locking para concorrência), `created_at`, `updated_at`.
- **FR-002**: O sistema DEVE expor endpoints RESTful exclusivos para admin listar, ativar e desativar features, protegidos por role-based access control (role Admin).
- **FR-003**: O sistema DEVE validar o status da feature (ativa/inativa) antes de processar qualquer requisição a ela, utilizando um middleware ou decorator de rota.
- **FR-004**: Cada feature DEVE ser autocontida em seu próprio diretório com: modelo de dados (se houver), serviços, rotas, schemas Pydantic e testes independentes.
- **FR-005**: O sistema DEVE persistir o estado das features em uma tabela PostgreSQL com migrações gerenciadas (Alembic ou similar).
- **FR-006**: O sistema DEVE fornecer um decorator/função de validação `require_feature(slug)` que, quando aplicado a uma rota, verifica se a feature está ativa e retorna erro 404/503 caso contrário.
- **FR-007**: Cada feature DEVE ter seu próprio conjunto de testes que pode ser executado isoladamente sem impactar outras features.
- **FR-008**: O sistema DEVE carregar o estado das features no startup da aplicação e armazenar em cache local para evitar consultas repetitivas ao banco.
- **FR-009**: O cache de features DEVE ter um TTL configurável (default 60 segundos) e ser invalidado quando um admin altera o status de uma feature.
- **FR-010**: O admin DEVE poder visualizar no painel: slug, nome, descrição, status atual, data de criação e última alteração de cada feature.

### Key Entities *(include if feature involves data)*

- **FeatureFlag**: Representa uma feature modular do sistema. Atributos: `id` (UUID), `slug` (identificador único, ex: "geracao-apostas"), `nome` (ex: "Geração de Apostas"), `descricao`, `ativa` (boolean), `created_at`, `updated_at`, `version` (controle de concorrência).
- **FeatureModule**: Estrutura de diretório autocontida contendo: `api/routes.py`, `services/`, `models.py` (se houver), `tests/`, `__init__.py`. Não é uma entidade de banco, mas um padrão arquitetural.
- **FeatureRegistry**: Singleton em memória que mantém o cache atualizado de todas as features e seus status, populado no startup e atualizado via eventos de invalidação.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O painel admin de features deve carregar a lista completa em menos de 200ms mesmo com 50+ features cadastradas.
- **SC-002**: A validação de feature ativa/inativa em uma requisição deve adicionar no máximo 5ms de overhead à resposta.
- **SC-003**: Uma alteração de status feita por um admin deve ser refletida em todas as instâncias em no máximo 60 segundos (TTL do cache).
- **SC-004**: Testes de uma feature modular devem poder ser executados isoladamente (`pytest tests/features/<feature>/`) sem executar ou falhar testes de outras features.
- **SC-005**: 100% das features existentes devem ser migradas para o formato modular sem quebra de funcionalidade.
- **SC-006**: Zero regressão: a implementação de uma nova feature modular não deve causar falha em nenhum teste de feature existente.

## Assumptions

- **Role Admin já implementada**: Assume-se que o sistema de autenticação e roles (Admin/Usuário) será implementado separadamente ou já existe como pré-requisito.
- **Cache em memória**: Assume-se que o cache local em memória é suficiente para o TTL de 60s; Redis pode ser adicionado futuramente se houver necessidade de invalidação instantânea em clusters maiores.
- **PostgreSQL como banco principal**: Assume-se que o banco PostgreSQL está disponível e as migrações serão gerenciadas com Alembic.
- **Migração progressiva**: Features existentes podem ser migradas para o formato modular gradualmente, não sendo obrigatório refatorar tudo de uma vez.
- **Template de feature**: Um diretório `features/_template/` será criado como blueprint para novas features, contendo a estrutura esperada de diretórios e arquivos.
