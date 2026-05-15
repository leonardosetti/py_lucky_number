# Feature Specification: System Management

**Feature Branch**: `003-system-management`
**Created**: 2026-05-11
**Status**: Draft
**Input**: User description: "Inclua uma especificação para a feature de system management; Esta feature deverá ser capaz de: Criar, Editar, Excluir, CLonar usuários, roles e permissions; Será capaz de habilitar ou desabilitar features específicas; Será capaz de Criar, Editar, Excluir, Clonar notificações do sistema para usuários/roles, será capaz de validar por dashboard o tracking de uso da aplicação por usuários grupos de usuários, por região por data, por range de valor de promessa de apostas; A estrutura de roles deve ser hierarquica, os usuários comuns (apostadores potenciais) serão criados via interface através do uso espontâneo da aplicação, devemos ter usuários para testes em d iferentes categorias de permissão; Roles: Admin (acesso total); Auditor (Acesso modo leitura de todas as features e configurações internas); TestDemo (acesso editável porém efêmero, não vai persistir mudanças para próximas sessões); Esta feature deve prezar pela segurança e robustez na implemetação; utilize travas de segurança para impedir deleção arbitrária de entidades e ou usaŕios admiinistradores"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin Gerencia Usuários, Roles e Permissões (Priority: P1)

Como um administrador do sistema, quero criar, editar, excluir e clonar usuários, roles e permissões através de um painel centralizado, para controlar quem tem acesso a cada funcionalidade do sistema de forma granular e hierárquica.

**Why this priority**: O gerenciamento de identidade e acesso é a fundação sobre a qual todas as outras capacidades administrativas (features, notificações, dashboard) são construídas. Sem roles e permissões, não há como restringir acesso.

**Independent Test**: Pode ser testado criando uma nova role com permissões específicas, associando um usuário a ela, e verificando que o usuário só consegue acessar os recursos permitidos pela role.

**Acceptance Scenarios**:

1. **Given** que o admin está autenticado, **When** ele cria um novo usuário com dados válidos (nome, email, role), **Then** o usuário é persistido no banco e retorna com ID único.
2. **Given** um usuário existente, **When** o admin edita seus dados ou altera sua role, **Then** as alterações são salvas imediatamente.
3. **Given** um usuário existente (não admin), **When** o admin solicita a exclusão, **Then** o usuário é marcado como inativo (soft delete) e removido da listagem ativa.
4. **Given** um usuário com role Admin, **When** qualquer tentativa de exclusão é feita, **Then** o sistema bloqueia a operação com erro de segurança.
5. **Given** um usuário ou role existente, **When** o admin clona a entidade, **Then** uma cópia exata é criada com novo ID e sufixo "(clone)" no nome.
6. **Given** uma role existente, **When** o admin edita suas permissões, **Then** todos os usuários vinculados àquela role têm seus acessos atualizados na próxima requisição.

---

### User Story 2 - Admin Gerencia Features do Sistema (Priority: P1)

Como um administrador, quero visualizar todas as features modulares do sistema e alternar seu estado (ativada/desativada) através do painel de gerenciamento, para controlar a disponibilidade de funcionalidades em produção sem deploy.

**Why this priority**: Esta capacidade integra diretamente com a feature Modular Feature System (002), formando o ciclo completo de gestão de features com toggle administrativo.

**Independent Test**: Pode ser testado desativando uma feature pelo painel admin e confirmando que o endpoint correspondente retorna indisponível para usuários não-admin.

**Acceptance Scenarios**:

1. **Given** a lista de features carregada no painel, **When** o admin alterna o toggle de uma feature, **Then** o estado é persistido e o cache de features é invalidado.
2. **Given** uma feature desativada pelo admin, **When** um usuário comum tenta acessá-la, **Then** o sistema retorna erro de recurso indisponível.

---

### User Story 3 - Admin Gerencia Notificações do Sistema (Priority: P2)

Como um administrador, quero criar, editar, excluir e clonar notificações direcionadas a usuários específicos ou roles inteiras, para comunicar manutenções, resultados de sorteios ou promoções de forma segmentada.

**Why this priority**: Notificações são um canal de comunicação direto com o usuário, mas o sistema funciona sem elas — daí prioridade P2.

**Independent Test**: Pode ser testado criando uma notificação direcionada a uma role, logando como usuário daquela role, e confirmando que a notificação aparece no painel do usuário.

**Acceptance Scenarios**:

1. **Given** que o admin cria uma notificação com título, mensagem, prioridade e destinatário (usuário ou role), **When** ele salva, **Then** a notificação é disparada para todos os destinatários elegíveis.
2. **Given** uma notificação existente, **When** o admin a edita, **Then** a versão editada substitui a anterior para novos acessos.
3. **Given** uma notificação existente, **When** o admin a exclui, **Then** ela é removida da visualização de todos os usuários.
4. **Given** uma notificação existente, **When** o admin a clona, **Then** uma cópia é criada com novos IDs e mesma configuração de destinatários.

---

### User Story 4 - Admin Visualiza Dashboard de Tracking de Uso (Priority: P2)

Como um administrador, quero acessar um dashboard com métricas de uso da aplicação filtradas por usuário, grupo de usuários, região, data e range de valor de promessa de apostas, para tomar decisões baseadas em dados sobre o negócio.

**Why this priority**: O dashboard fornece inteligência de negócio, mas não é crítico para o funcionamento do sistema — daí P2.

**Independent Test**: Pode ser testado gerando algumas apostas e promessas via API, acessando o dashboard com filtros, e validando que os números exibidos correspondem aos dados gerados.

**Acceptance Scenarios**:

1. **Given** dados de uso registrados no sistema, **When** o admin acessa o dashboard sem filtros, **Then** o sistema exibe métricas agregadas totais (usuários ativos, apostas geradas, promessas criadas, features mais acessadas).
2. **Given** o dashboard carregado, **When** o admin aplica filtro por data (início/fim), **Then** as métricas são recalculadas apenas para o período selecionado.
3. **Given** o dashboard carregado, **When** o admin aplica filtro por região geográfica, **Then** as métricas são filtradas para aquela região.
4. **Given** o dashboard carregado, **When** o admin aplica filtro por range de valor de promessa (ex: R$10-R$100), **Then** apenas promessas naquele range são contabilizadas.
5. **Given** o dashboard carregado, **When** o admin aplica filtro por usuário ou role específica, **Then** as métricas refletem apenas a atividade daquele usuário/grupo.

---

### User Story 5 - Auditor Visualiza Configurações em Modo Leitura (Priority: P3)

Como um auditor, quero acessar todas as telas de configuração do sistema em modo somente leitura, para verificar conformidade e rastrear alterações sem poder modificar nada.

**Why this priority**: Auditoria é importante para compliance, mas não impacta a operação diária do sistema.

**Independent Test**: Pode ser testado logando como Auditor, acessando páginas de admin e confirmando que todos os botões de ação (criar, editar, excluir) estão desabilitados ou ausentes.

**Acceptance Scenarios**:

1. **Given** que um usuário com role Auditor está autenticado, **When** ele acessa o painel de gerenciamento de usuários, **Then** ele pode visualizar todos os dados mas não consegue criar, editar ou excluir.
2. **Given** um Auditor no dashboard de tracking, **When** ele aplica filtros, **Then** os dados são exibidos normalmente, mas não há opção de exportar configurações.

---

### User Story 6 - Usuário TestDemo Opera em Modo Efêmero (Priority: P3)

Como um usuário com role TestDemo, quero poder testar todas as funcionalidades do sistema como se tivesse permissão total, mas sem que nenhuma alteração seja persistida entre sessões, para validar comportamentos sem risco de impacto ao sistema real.

**Why this priority**: TestDemo acelera homologação, mas não é essencial para o funcionamento do sistema.

**Independent Test**: Pode ser testado logando como TestDemo, criando dados, fazendo logout, logando novamente, e confirmando que os dados criados na sessão anterior não existem mais.

**Acceptance Scenarios**:

1. **Given** que um usuário TestDemo está autenticado, **When** ele cria, edita ou exclui qualquer entidade, **Then** as operações são executadas normalmente durante a sessão, mas marcadas como efêmeras.
2. **Given** que um usuário TestDemo criou dados em uma sessão anterior, **When** ele inicia uma nova sessão, **Then** os dados da sessão anterior não estão mais disponíveis.
3. **Given** que um usuário TestDemo está ativo, **When** sua sessão expira (timeout de 8 horas), **Then** todos os dados criados por ele são automaticamente removidos.

---

### Edge Cases

- **Proteção contra auto-exclusão**: Nenhum usuário pode excluir a si mesmo. A tentativa deve ser bloqueada com erro explícito.
- **Último admin**: O sistema deve impedir a remoção da role Admin do último usuário com essa role. Pelo menos um admin deve existir sempre.
- **Notificação órfã**: Se uma notificação é direcionada a uma role que foi excluída, a notificação deve ser marcada como "destinatário removido" mas mantida para auditoria.
- **Clone de role com permissões**: Ao clonar uma role, as permissões associadas devem ser clonadas também (cópia rasa das permissões, não referência).
- **Sessão TestDemo concorrente**: Um usuário TestDemo não pode ter duas sessões ativas simultaneamente.
- **Dashboard sem dados**: O dashboard deve exibir estado vazio com mensagem amigável quando não há dados para o filtro selecionado, nunca um erro.
- **Região não identificada**: Se a região do usuário não puder ser determinada, o sistema deve agrupar como "Região não identificada" nos dashboards.
- **Filtro de data inválido**: Se a data final for anterior à data inicial, o sistema deve ignorar o filtro e exibir todas as datas ou exibir erro amigável.

## Requirements *(mandatory)*

### Functional Requirements

**User, Role & Permission Management**
- **FR-001**: O sistema DEVE permitir que admins criem, leiam, editem, excluam (soft delete) e clonem usuários.
- **FR-002**: O sistema DEVE permitir que admins criem, leiam, editem, excluam e clonem roles com permissões associadas.
- **FR-003**: A estrutura de roles DEVE ser hierárquica — roles podem herdar permissões de roles superiores, e uma role filha não pode ter mais permissões que a role pai.
- **FR-004**: O sistema DEVE bloquear a exclusão de usuários com role Admin (erro de segurança).
- **FR-005**: O sistema DEVE bloquear a exclusão ou rebaixamento do último usuário com role Admin.
- **FR-006**: O sistema DEVE bloquear a auto-exclusão do próprio usuário logado.
- **FR-007**: O sistema DEVE implementar soft delete para usuários (flag `ativo` = false), preservando o registro no banco para auditoria.
- **FR-008**: O sistema DEVE permitir a criação espontânea de contas de usuário (apostadores) via interface pública com validação de email.
- **FR-009**: O sistema DEVE permitir a criação de usuários de teste (role TestDemo) com dados pré-configurados em diferentes categorias de permissão.
- **FR-010**: A role Admin DEVE ter acesso total e irrestrito a todas as funcionalidades do sistema.
- **FR-011**: A role Auditor DEVE ter acesso somente leitura a todas as features e configurações internas, sem qualquer ação de escrita.
- **FR-012**: A role TestDemo DEVE ter permissão de escrita, mas todas as alterações DEVEM ser efêmeras. O mecanismo padrão é **transaction rollback**: todas as operações do TestDemo rodam em uma transação que é revertida ao final da sessão (logout ou timeout de 8 horas). Dados criados não persistem entre sessões.
- **FR-013**: A role comum (apostador) DEVE ter acesso apenas às features de geração de apostas, visualização de resultados e gerenciamento de promessas pessoais.

**Feature Toggle Management**
- **FR-014**: O sistema DEVE expor no painel admin a lista completa de features modulares com toggle para ativar/desativar cada uma.
- **FR-015**: A alteração de status de uma feature DEVE invalidar o cache de features e refletir imediatamente nas validações de acesso.

**Notification Management**
- **FR-016**: O sistema DEVE permitir que admins criem notificações com: título, mensagem, prioridade (Alta/Média/Baixa), destinatário (usuário específico ou role).
- **FR-017**: O sistema DEVE permitir que admins editem, excluam e clonem notificações existentes.
- **FR-018**: As notificações DEVEM ser exibidas no painel do usuário destinatário na próxima requisição autenticada.
- **FR-019**: As notificações DEVEM ter data de expiração opcional — notificações expiradas não são exibidas.

**Dashboard de Tracking**
- **FR-020**: O sistema DEVE registrar eventos de uso: login, geração de aposta, criação de promessa, acesso a features.
- **FR-021**: O dashboard DEVE exibir métricas agregadas: total de usuários ativos, total de apostas geradas (por período), total de promessas criadas, features mais acessadas.
- **FR-022**: O dashboard DEVE suportar filtros combináveis: por usuário, por role/grupo de usuários, por região geográfica, por range de datas, por range de valor de promessa.
- **FR-023**: Os filtros do dashboard DEVEM ser combináveis entre si (ex: usuário X + região Y + mês Z).
- **FR-024**: O dashboard DEVE exibir estado vazio quando não há dados para os filtros aplicados.

**Segurança e Robustez**
- **FR-025**: O sistema DEVE exigir confirmação explícita (segundo passo) para operações de exclusão de usuários, roles e notificações.
- **FR-026**: O sistema DEVE auditar e logar todas as operações de criação, edição e exclusão realizadas por admins, com timestamp e identificação do admin responsável.
- **FR-027**: O sistema DEVE implementar rate limiting nas operações de gerenciamento (máximo de 30 requisições por minuto por admin).

### Key Entities

- **User**: Representa um usuário do sistema. Atributos: `id` (UUID), `nome`, `email` (único), `senha_hash`, `role_id` (FK), `regiao` (opcional), `ativo` (boolean), `created_at`, `updated_at`, `deleted_at` (soft delete).
- **Role**: Representa um perfil de permissão hierárquico. Atributos: `id` (UUID), `nome` (único, ex: "Admin", "Auditor", "TestDemo"), `descricao`, `parent_role_id` (auto-FK para hierarquia), `created_at`, `updated_at`.
- **Permission**: Representa uma permissão atômica. Atributos: `id` (UUID), `slug` (ex: "users.create", "features.toggle"), `nome`, `descricao`, `recurso` (ex: "users", "features", "notifications").
- **RolePermission**: Associação N:N entre Role e Permission. Atributos: `role_id`, `permission_id`, `granted` (boolean — true para permitir, false para negar explicitamente).
- **SystemNotification**: Representa uma notificação do sistema. Atributos: `id` (UUID), `titulo`, `mensagem`, `prioridade`, `destinatario_user_id` (nullable), `destinatario_role_id` (nullable), `data_expiracao` (nullable), `created_at`, `updated_at`, `created_by` (admin que criou).
- **NotificationDelivery**: Registro individual de entrega. Atributos: `id` (UUID), `notification_id` (FK), `user_id` (FK), `lida` (boolean), `lida_em` (timestamp).
- **UsageEvent**: Evento de uso registrado para tracking. Atributos: `id` (UUID), `user_id` (FK), `event_type` (login, geracao_aposta, criacao_promessa, etc.), `metadata` (JSON com detalhes), `regiao` (inferido do request), `created_at`.
- **FeatureToggle**: Registro de feature modular (mesma entidade da spec 002). Atributos: `id` (UUID), `slug`, `nome`, `descricao`, `ativa`, `created_at`, `updated_at`.
- **AuditLog**: Log de auditoria para operações administrativas. Atributos: `id` (UUID), `admin_id` (FK), `acao` (create/update/delete/clone), `entidade_tipo` (user/role/notification/feature), `entidade_id`, `detalhes` (JSON com diff/valores anteriores), `created_at`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um admin consegue criar um novo usuário com role e permissões em menos de 60 segundos.
- **SC-002**: A exclusão de um usuário admin ou do último admin é bloqueada 100% das vezes com mensagem de erro clara.
- **SC-003**: Todas as 3 roles predefinidas (Admin, Auditor, TestDemo) funcionam conforme especificado sem necessidade de configuração adicional.
- **SC-004**: Notificações criadas para uma role são visíveis para todos os usuários daquela role em menos de 5 segundos.
- **SC-005**: O dashboard de tracking carrega em menos de 2 segundos mesmo com 100.000+ eventos registrados.
- **SC-006**: A combinação de 3+ filtros no dashboard retorna resultados consistentes em menos de 3 segundos.
- **SC-007**: Dados criados por usuários TestDemo são completamente removidos em até 5 minutos após o término da sessão.
- **SC-008**: Nenhuma operação de escrita de um usuário Auditor persiste no sistema (0% de taxa de persistência acidental).
- **SC-009**: Todas as operações administrativas são registradas no log de auditoria com 100% de rastreabilidade.

## Assumptions

- **Feature Modular System (002) implementado**: Assume-se que o sistema de features modulares com toggle já existe como pré-requisito, incluindo a tabela `feature_flags` e o middleware de validação.
- **Autenticação JWT existente**: Assume-se que o sistema de autenticação com JWT e extração de roles já está implementado.
- **Geolocalização por IP**: A região do usuário será inferida a partir do endereço IP da requisição (biblioteca GeoIP), sem exigir cadastro explícito de localização.
- **Soft delete como padrão**: Todas as exclusões de entidades administrativas (usuários, roles, notificações) usam soft delete com flag `ativo` ou `deleted_at`, exceto limpeza de dados TestDemo.
- **Sessão TestDemo**: A sessão TestDemo tem duração máxima de 8 horas corridas, após as quais todos os dados criados são limpos por job agendado.
- **Dados de teste iniciais**: O sistema será entregue com seeds de dados contendo: 3 roles (Admin, Auditor, TestDemo), permissões pré-definidas, e usuários de exemplo em cada role.
- **Hierarquia de roles**: A hierarquia é definida por `parent_role_id`. A role Admin não tem parent (topo da hierarquia). Roles filhas herdam permissões da role pai mas não podem excedê-las.
