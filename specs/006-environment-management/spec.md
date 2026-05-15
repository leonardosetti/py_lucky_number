# Feature Specification: Environment Management

**Feature Branch**: `006-environment-management`
**Created**: 2026-05-11
**Status**: Draft
**Input**: User description: "Crie uma especificação de demanda de ambientes, precisamos de ambientes distintos para desenvolvimento contínuo, bug fixes, testes, demo, produção. Este contexto deverá refletir na estrutura do github cada qual com sua branch específica. Implementações futuras deverão ter sua própria branch para merge posterior."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Desenvolvedor Trabalha em Feature com Isolamento Total (Priority: P1)

Como desenvolvedor, quero criar uma branch de feature a partir da develop, implementar e testar localmente em container isolado, e ao final abrir um Pull Request para merge em develop, para garantir que meu código não afete outros desenvolvedores ou ambientes compartilhados durante o desenvolvimento.

**Why this priority**: O isolamento por branch + container é a base do fluxo de trabalho. Sem ele, desenvolvedores interferem entre si e quebram o ambiente compartilhado.

**Independent Test**: Pode ser testado criando uma branch `feature/test-isolation`, modificando um arquivo, e confirmando que o ambiente `development` compartilhado não reflete as alterações até o merge.

**Acceptance Scenarios**:

1. **Given** um repositório configurado com gitflow, **When** um desenvolvedor cria `feature/nova-funcionalidade` a partir de `develop`, **Then** a branch contém todo o código base mais as alterações da feature, sem impactar `develop` ou `main`.
2. **Given** uma branch de feature, **When** o desenvolvedor executa `docker compose up` com perfil `dev`, **Then** os containers da feature rodam isolados com seus próprios volumes de dados, sem conflito com outros containers.
3. **Given** uma feature completa e testada, **When** o desenvolvedor abre um Pull Request de `feature/*` para `develop`, **Then** a pipeline CI executa testes automatizados contra o banco de testes antes de permitir o merge.

---

### User Story 2 - Equipe de QA Valida Bug Fix em Ambiente de Testes (Priority: P1)

Como um analista de QA, quero que correções de bugs (hotfixes) sigam um fluxo acelerado: branch a partir de `main`, deploy em ambiente de testes para validação, e merge direto de volta para `main` e `develop`, para que bugs críticos sejam corrigidos e validados rapidamente sem passar por todo o ciclo de features.

**Why this priority**: Bugs em produção precisam de correção rápida. Um fluxo de hotfix bem definido reduz o MTTR (Mean Time to Repair).

**Independent Test**: Pode ser testado simulando um bug crítico, criando um hotfix, deployando no ambiente de testes, validando a correção, e fazendo o merge para main.

**Acceptance Scenarios**:

1. **Given** um bug crítico reportado em produção, **When** o desenvolvedor cria `hotfix/correcao-urgente` a partir de `main`, **Then** a branch contém apenas as alterações necessárias para a correção.
2. **Given** um hotfix implementado, **When** a pipeline CI executa, **Then** os testes são executados e, se aprovados, o deploy automático é feito no ambiente de testes para validação da equipe QA.
3. **Given** um hotfix validado em testes, **When** o merge é feito para `main` e `develop`, **Then** a pipeline de produção é acionada com deploy automático e tag de versão (patch).

---

### User Story 3 - Stakeholder Visualiza Funcionalidades no Ambiente de Demo (Priority: P2)

Como um stakeholder ou product owner, quero acessar um ambiente de demonstração estável contendo as últimas funcionalidades aprovadas em develop, com dados sintéticos realistas, para validar funcionalidades, dar feedback e demonstrar o progresso para clientes ou investidores sem expor dados reais ou código instável.

**Why this priority**: O ambiente demo é vital para alinhamento com stakeholders, mas não impacta o fluxo de desenvolvimento — daí P2.

**Independent Test**: Pode ser testado fazendo deploy automático de `develop` no ambiente demo e validando que as últimas funcionalidades mergeadas estão acessíveis com dados sintéticos.

**Acceptance Scenarios**:

1. **Given** que um merge para `develop` foi concluído, **When** a pipeline CI/CD detecta a alteração, **Then** o ambiente demo é automaticamente atualizado com a nova versão.
2. **Given** o ambiente demo disponível, **When** um stakeholder acessa a URL, **Then** o sistema está funcional com dados sintéticos (nunca dados reais de produção).
3. **Given** uma sessão no ambiente demo, **When** o usuário interage com o sistema, **Then** as alterações são efêmeras e não persistem entre sessões (reset diário).

---

### User Story 4 - Administrador Promove Versão para Produção (Priority: P1)

Como administrador do sistema, quero que o ambiente de produção receba apenas código aprovado e mergeado em `main`, com deploy automatizado porém com gate de aprovação manual, garantindo que nenhuma alteração não testada chegue aos usuários finais.

**Why this priority**: Produção é o ambiente crítico. Um deploy quebrado afeta todos os usuários. A validação manual é a última barreira de segurança.

**Independent Test**: Pode ser testado simulando um merge para `main` e validando que o deploy para produção só ocorre após aprovação manual explícita.

**Acceptance Scenarios**:

1. **Given** um merge aprovado em `main`, **When** a pipeline de produção é acionada, **Then** ela executa todos os testes, valida migrações (dry-run), e pausa para aprovação manual antes do deploy efetivo.
2. **Given** o deploy em produção autorizado, **When** executado, **Then** os containers de produção são atualizados sem downtime (rolling update) e com health check antes de cortar tráfego.
3. **Given** o deploy em produção completo, **When** verificado, **Then** o ambiente de produção está rodando a nova versão e todos os health checks passam.

---

## Git Branch Strategy

```
main
  ├── develop
  │    ├── feature/nova-aposta        ← criada de develop, merge → develop
  │    ├── feature/relatorio-dashboard ← criada de develop, merge → develop
  │    └── feature/export-csv         ← criada de develop, merge → develop
  ├── hotfix/corrige-login          ← criada de main, merge → main + develop
  ├── release/v1.2.0                ← criada de develop, merge → main
  └── bugfix/ajusta-css             ← criada de develop, merge → develop
```

### Branch Rules

| Branch | Origem | Destino | Propósito | Ambiente |
|---|---|---|---|---|
| `main` | — | — | Código de produção, estável | Produção |
| `develop` | `main` | `main` (via release) | Integração contínua, próximo release | Demo |
| `feature/*` | `develop` | `develop` (via PR) | Nova funcionalidade | Desenvolvimento (local) |
| `hotfix/*` | `main` | `main` + `develop` | Correção urgente em produção | Testes + Produção |
| `bugfix/*` | `develop` | `develop` (via PR) | Correção não urgente | Desenvolvimento |
| `release/*` | `develop` | `main` | Preparação de versão | Testes + Pré-produção |

### Protection Rules (GitHub)

- `main`: ⛔ Protegida — sem pushes diretos. Apenas PR com aprovação de 1 reviewer + CI verde.
- `develop`: ⛔ Protegida — sem pushes diretos. Apenas PR com CI verde.
- `feature/*`: ✅ Pushes diretos permitidos. Nome padronizado: `feature/<slug-curto>`.
- `hotfix/*`: ⛔ Apenas admins podem criar. Merge exige aprovação de 2 reviewers + CI verde.

---

## Environment Architecture

### Environment Map

| Ambiente | Branch Fonte | Deploy | Banco de Dados | Dados | Público |
|---|---|---|---|---|---|
| **Desenvolvimento** (local) | `feature/*` | `docker compose up --profile dev` | PostgreSQL container (volátil) | Seed mínimo + dados de teste | Não (localhost) |
| **Testes** (CI/CD) | `feature/*` ou `develop` | Pipeline CI isolada | PostgreSQL recriado por execução | Seed de teste | Não (isolado) |
| **Demo** | `develop` | Automático (após merge) | PostgreSQL container persistente | Dados sintéticos (Faker) | Sim (URL pública) |
| **Produção** | `main` | Manual (com aprovação) | PostgreSQL gerenciado (RDS/Cloud SQL) | Dados reais | Sim (domínio oficial) |

### Docker Container Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   docker-compose.yml                     │
│                                                          │
│  profiles:                                               │
│    dev:     api + db-dev       (feature isolation)       │
│    demo:    api + db-demo      (stable demo)             │
│    test:    api + db-test      (CI ephemeral)            │
│    prod:    api + db-prod      (production)              │
│                                                          │
│  Volumes:                                                │
│    pgdata-dev    → persistente (dev local)               │
│    pgdata-demo   → persistente (demo público)            │
│    pgdata-prod   → gerenciado externo (RDS/Cloud SQL)    │
│    pgdata-test   → volátil (recriado a cada execução)    │
└─────────────────────────────────────────────────────────┘
```

### Volume & Data Persistence Strategy

| Ambiente | Volume | Persistência | Ciclo de Vida |
|---|---|---|---|
| Dev (local) | `pgdata-dev` | ✅ Sim, entre sessões locais | Manual: `docker compose down -v` para reset |
| Testes | Nenhum (ephemeral) | ❌ Não | Recriado a cada execução de teste |
| Demo | `pgdata-demo` | ✅ Sim, entre deploys | Reset manual ou automatizado (diário) |
| Produção | Volume gerenciado externo | ✅ Sim, backups diários | Gerenciado pelo provedor de cloud |

### Maintainability Considerations

1. **Separação de concerns por Docker Compose profile**: Cada ambiente usa o mesmo `docker-compose.yml` mas com profiles diferentes. Isso elimina duplicação de configuração.
2. **Imagens reutilizáveis**: A mesma imagem Docker da aplicação é promovida entre ambientes (test → demo → prod), garantindo que o artefato testado é o mesmo deployado.
3. **Volumes nomeados**: Volumes `pgdata-*` são nomeados e não anônimos, facilitando backup, restore e identificação.
4. **Sem dados reais fora da produção**: Ambientes não-prod usam seeds sintéticos, eliminando risco de vazamento de dados.
5. **Rolling update em produção**: O deploy em produção usa estratégia de rolling update com health check, sem downtime.

---

## Requirements *(mandatory)*

### Functional Requirements

**Git Branch Strategy**
- **FR-001**: O repositório DEVE seguir a estratégia gitflow com branches `main`, `develop`, `feature/*`, `hotfix/*`, `bugfix/*` e `release/*`.
- **FR-002**: A branch `main` DEVE ser protegida (sem pushes diretos, apenas PR com 1 approval + CI verde).
- **FR-003**: A branch `develop` DEVE ser protegida (sem pushes diretos, apenas PR com CI verde).
- **FR-004**: Branches `feature/*` DEVEM ser criadas a partir de `develop` e mergeadas de volta para `develop` via Pull Request.
- **FR-005**: Branches `hotfix/*` DEVEM ser criadas a partir de `main` e mergeadas para `main` e `develop` simultaneamente.
- **FR-006**: Branches `release/*` DEVEM ser criadas a partir de `develop` e mergeadas para `main` com tag de versão semântica.

**Environment Management**
- **FR-007**: O sistema DEVE definir 4 ambientes distintos: desenvolvimento, testes, demo e produção.
- **FR-008**: Cada ambiente DEVE ter seu próprio banco de dados PostgreSQL isolado dos demais.
- **FR-009**: O ambiente demo DEVE ser atualizado automaticamente após cada merge em `develop`.
- **FR-010**: O ambiente de produção DEVE ser atualizado apenas via aprovação manual, nunca automaticamente.
- **FR-011**: O ambiente de testes DEVE ser efêmero — recriado do zero a cada execução de pipeline.
- **FR-012**: O ambiente demo NUNCA DEVE conter dados reais de produção — apenas dados sintéticos.

**Docker & Containerization**
- **FR-013**: A aplicação DEVE ser containerizada com imagem Docker única e reutilizável entre ambientes.
- **FR-014**: O `docker-compose.yml` DEVE usar profiles (`dev`, `demo`, `test`, `prod`) para selecionar o ambiente.
- **FR-015**: Cada ambiente DEVE ter seu próprio volume nomeado para persistência de dados do banco.
- **FR-016**: O container do banco de dados DEVE usar imagem PostgreSQL oficial com volume persistente separado.
- **FR-017**: O deploy em produção DEVE usar rolling update com health check para zero downtime.
- **FR-018**: O ambiente de desenvolvimento local DEVE ser iniciável com um único comando (`make dev` ou `docker compose --profile dev up`).

**CI/CD Pipeline**
- **FR-019**: A pipeline de CI DEVE executar testes, linters e validação de migrações contra o banco de testes.
- **FR-020**: A pipeline de CD DEVE construir a imagem Docker uma única vez e promovê-la entre ambientes (build once, deploy many).
- **FR-021**: O deploy em produção DEVE exigir aprovação manual com gate de qualidade (CI verde + migrações validadas).
- **FR-022**: O deploy no ambiente demo DEVE ser automático após merge em `develop`, sem aprovação manual.
- **FR-023**: A pipeline DEVE executar validação de segurança (scanner de vulnerabilidades na imagem) antes do deploy em produção.
- **FR-024**: Cada merge em `main` DEVE gerar uma tag de versão semântica automática (vMAJOR.MINOR.PATCH).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um novo desenvolvedor configura o ambiente local completo (containers + banco + seed) em menos de 10 minutos com um único comando.
- **SC-002**: O ciclo completo de uma feature (branch → implementação → PR → CI → merge → demo) é concluído em menos de 30 minutos para alterações simples.
- **SC-003**: O ambiente demo está sempre sincronizado com a branch `develop` com no máximo 5 minutos de atraso após o merge.
- **SC-004**: Zero downtime em deploys de produção — 100% dos deploys são concluídos sem interromper o serviço.
- **SC-005**: 100% dos deploys em produção passam por aprovação manual antes de serem executados.
- **SC-006**: 95% dos bugs críticos são corrigidos e deployados em produção em menos de 4 horas (hotfix flow).
- **SC-007**: Ambientes não-prod nunca contêm dados reais de produção — verificado por scanner automatizado semanal.

## Assumptions

- **Docker e Docker Compose instalados**: Assume-se que Docker 24+ e Docker Compose v2 estão disponíveis em todos os ambientes (dev, CI, servidores).
- **GitHub como plataforma Git**: Assume-se o uso de GitHub para repositório, proteção de branches e Actions para CI/CD.
- **Semântica de versão (SemVer)**: Versões seguem o padrão MAJOR.MINOR.PATCH conforme resultados dos merges em `main`.
- **Container registry**: Assume-se um registry de containers (Docker Hub, GHCR, ECR) para armazenar e promover imagens entre ambientes.
- **Banco gerenciado em produção**: Produção usa PostgreSQL gerenciado (RDS, Cloud SQL, etc.) com backups automáticos. Containers PostgreSQL são apenas para dev/demo/teste.
- **Health check endpoint**: A aplicação FastAPI expõe `/api/v1/health` que valida conexão com banco e retorna status 200 quando pronto.
- **Variáveis de ambiente por ambiente**: Cada ambiente tem seu próprio arquivo `.env.<ambiente>` (`.env.dev`, `.env.demo`, `.env.prod`) com as configurações específicas.
