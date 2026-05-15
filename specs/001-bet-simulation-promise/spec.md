# Feature Specification: Simulação de Valor Acumulado e Promessa de Aposta

**Feature Branch**: `SIM-001-bet-simulation-promise`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Simulação de Valor Acumulado e Promessa de Aposta"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Seleção de Apostas e Cálculo de Valor (Priority: P1)

Como um apostador (registrado ou anônimo), quero selecionar múltiplas combinações de diferentes loterias e ver o custo total instantaneamente para planejar meus gastos.

**Why this priority**: Esta é a funcionalidade central da feature; sem o cálculo do valor, a "Promessa de Aposta" perde seu propósito principal de planejamento financeiro.

**Independent Test**: Pode ser testado selecionando 3 combinações de modalidades diferentes e validando se a soma dos preços individuais bate com o total exibido na tela.

**Acceptance Scenarios**:

1. **Given** que o usuário está visualizando a lista de combinações, **When** ele marca 2 apostas da Mega-Sena (6 números) e 1 da Lotofácil (15 números), **Then** o sistema deve exibir o total de R$ 15,50 dinamicamente.
2. **Given** que existem combinações selecionadas, **When** o usuário clica em "Desmarcar todas", **Then** o valor total deve retornar a R$ 0,00 imediatamente.

---

### User Story 2 - Criação e Armazenamento de Promessa (Priority: P2)

Como um usuário, quero salvar minha seleção atual com um título e prioridade para que eu possa resgatá-la futuramente sem precisar selecionar tudo novamente.

**Why this priority**: Permite a persistência do planejamento, transformando a simulação efêmera em um registro útil.

**Independent Test**: Pode ser testado criando uma promessa com título "Aposta Final de Semana", prioridade "Alta", e verificando se ela aparece corretamente na página "Minhas Promessas".

**Acceptance Scenarios**:

1. **Given** que o usuário tem combinações selecionadas, **When** ele clica em "Salvar Promessa" e preenche os dados no modal, **Then** o sistema deve persistir a promessa com um snapshot das combinações, título e prioridade.
2. **Given** que um usuário registrado já possui 50 promessas, **When** ele salva a 51ª, **Then** a promessa mais antiga que não seja favorita deve ser excluída automaticamente (FIFO).

---

### User Story 3 - Gerenciamento e Compartilhamento de Promessas (Priority: P3)

Como um usuário, quero organizar minhas promessas por prioridade, favoritá-las e compartilhá-las com outros via link temporário.

**Why this priority**: Adiciona valor de organização e socialização, mas o sistema é funcional sem essas capacidades.

**Independent Test**: Pode ser testado gerando um link de compartilhamento para uma promessa e abrindo esse link em uma aba anônima para validar a visualização dos dados.

**Acceptance Scenarios**:

1. **Given** a página "Minhas Promessas", **When** o usuário aplica o filtro de prioridade "Alta", **Then** apenas as promessas marcadas como alta prioridade devem ser exibidas.
2. **Given** uma promessa salva, **When** o usuário gera um link de compartilhamento, **Then** qualquer pessoa com o link deve conseguir visualizar as combinações daquela promessa por até 7 dias.

### Edge Cases

- **Regra de Preço Alterada**: Se a CAIXA alterar o preço de uma modalidade após a promessa ter sido salva, o valor da promessa (snapshot) permanece inalterado, mas o usuário deve ter a opção de "recriar" a promessa para atualizar os valores.
- **Sessão Anônima Expirada**: Se um usuário anônimo criar uma promessa e o cookie de sessão expirar após 30 dias, a promessa deve ser permanentemente removida do sistema.
- **Combinações Deletadas**: Se o usuário deletar da sua conta as combinações que compunham uma promessa, a promessa deve permanecer intacta, pois ela armazena um snapshot (cópia) e não apenas referências.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE implementar o cálculo de preço para cada modalidade seguindo rigorosamente as fórmulas da Constitution (Anexo SDD).
- **FR-002**: O sistema DEVE permitir a seleção e deseleção de combinações via interface (checkboxes) com atualização de total em tempo real (reativa).
- **FR-003**: O sistema DEVE persistir "Promessas de Aposta" contendo: UUID, ID do usuário/sessão, título, prioridade (Alta/Média/Baixa), valor total e um snapshot JSON das combinações.
- **FR-004**: O sistema DEVE implementar a política FIFO para o limite de 50 promessas por usuário, protegendo registros marcados como "favoritos".
- **FR-005**: O sistema DEVE gerar links de compartilhamento assinados (HMAC) com validade de 7 dias para visualização pública de promessas.
- **FR-006**: O sistema DEVE associar promessas de usuários anônimos a um `session_id` com expiração automática de 30 dias.

### Key Entities *(include if feature involves data)*

- **BetPromise (Promessa de Aposta)**: Representa a intenção de aposta. Atributos: ID único, Usuário/Sessão, Título, Prioridade, Valor Total, Snapshot de Combinações (JSON), Data de Criação, Status de Favorito.
- **CombinationSnapshot**: Cópia simplificada da combinação no momento da promessa. Atributos: Modalidade, Números, Trevos (se houver), Preço Individual.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O cálculo do valor total para até 100 combinações selecionadas deve ser processado e refletido na UI em menos de 50ms.
- **SC-002**: 100% das promessas salvas devem manter a integridade dos preços no snapshot, independentemente de alterações futuras nas tabelas de preços globais.
- **SC-003**: O link de compartilhamento deve permitir a visualização instantânea da promessa sem exigir autenticação do destinatário.
- **SC-004**: A exclusão automática (FIFO) deve ser disparada imediatamente ao tentar salvar a 51ª promessa para usuários registrados.

## Assumptions

- **Preços Estáticos por Snapshot**: Assume-se que a Promessa é um "contrato" do momento; mudanças de preços oficiais não alteram promessas antigas a menos que o usuário solicite explicitamente a atualização.
- **Autenticação**: Assume-se que o sistema de gestão de sessões (JWT/Cookies) já está implementado para diferenciar usuários registrados de anônimos.
- **Segurança de Links**: Assume-se que a visualização via link de compartilhamento é apenas de leitura (read-only) e não permite alteração da promessa.
- **Sincronismo**: Requisitos de UI para "atualização dinâmica" assumem o uso de frameworks reativos (como React/Vue) conforme definido na Constitution.
