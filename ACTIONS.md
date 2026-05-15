# Project Normalization — Action Plan

> Ações corretivas necessárias para normalizar inconsistências entre Constitution,
> Specs e Plan antes de avançar para tarefas de implementação (`/speckit.tasks` e
> `/speckit.implement`).
>
> Baseado na Análise de Consistência entre os 17 specs, Constitution v1.2.0 e
> Plan v0.1-beta. Gerado em: 2026-05-14.

---

## Priorização

| Prioridade | Critério |
|---|---|
| **P0** | Bloqueia qualquer implementação — Constitution violation ou spec ausente |
| **P1** | Impacta a correção estrutural do projeto — deve ser resolvido antes de tasks |
| **P2** | Melhoria necessária mas não bloqueia o início da implementação |
| **P3** | Pode ser resolvido durante a implementação |

---

## A01 — Recuperar FR-001 a 027 na Spec 004 (P0)

**Problema**: A spec 004 foi substituída pela v2.0 e perdeu os 27 requisitos
funcionais originais (ambientes, migrações, data integrity, segurança).

**Complexidade**: BAIXA  
**Tempo estimado**: 30 min  
**Arquivos afetados**: `specs/004-database-architecture/spec.md`

### Passos

1. Localizar o backup da spec 004 original no histórico do git:
   ```bash
   git log --all --oneline -- specs/004-database-architecture/spec.md
   git show <hash_anterior> > /tmp/spec-004-original.md
   ```
   Se não houver histórico, reconstruir a partir das specs 005 e 006
   (que contêm requisitos de ambiente e CI/CD que pertenciam à spec 004)

2. Extrair FR-001 a FR-027 do documento original.

3. Mesclar com FR-028 a FR-035 (atuais) em ordem sequencial (FR-001 a FR-035).

4. Validar que não há duplicação entre FRs originais e novos.

5. Atualizar `checklists/requirements.md` com o total de 35 FRs.

### Critério de aceite
- Spec 004 contém FR-001 a FR-035 sequenciais e sem gaps
- Nenhum FR duplicado ou conflitante

---

## A02 — Criar Spec 019 — Export & Share (P0)

**Problema**: Constitution Princípio VI exige exportação CSV/JSON/PDF +
compartilhamento WhatsApp/e-mail/cópia. Nenhuma spec existe.

**Complexidade**: MÉDIA  
**Tempo estimado**: 1h  
**Arquivos a criar**: `specs/019-export-share/spec.md`, `specs/019-export-share/checklists/requirements.md`

### Passos

1. Executar `/speckit.specify` com descrição detalhada baseada na Constitution VI:
   - Formatos: CSV, JSON, PDF
   - WhatsApp: link `wa.me` com mensagem pré-formatada
   - Entre usuários registrados: envio por ID interno com notificação
   - Cópia para área de transferência
   - Controle de acesso (próprias combinações)

2. Preencher user stories (P1: exportação individual, P2: compartilhamento
   entre usuários, P3: link público temporário)

3. Definir entidades: `ExportJob`, `ShareLink`

4. Validar checklist de qualidade.

### Critério de aceite
- `specs/019-export-share/spec.md` completo, 0 [NEEDS CLARIFICATION]
- Cobre todos os formatos e canais da Constitution VI

---

## A03 — Criar Spec 020 — Web Frontend (P0)

**Problema**: Constitution VII exige aplicação web responsiva. Apenas backend
implementado.

**Complexidade**: ALTA  
**Tempo estimado**: 2h  
**Arquivos a criar**: `specs/020-web-frontend/spec.md`, `specs/020-web-frontend/checklists/requirements.md`

### Passos

1. Executar `/speckit.specify` com descrição baseada na Constitution VII:
   - Framework: React + Next.js (SSR opcional) ou Vue.js com PWA
   - Design responsivo mobile-first
   - Telas: login/registro, geração de apostas, resultados, admin
   - Tema claro/escuro, paginação (20/página), acessibilidade WCAG 2.1 AA
   - Feedback visual para ações (exclusão, erro, limite)

2. Definir arquitetura de componentes:
   - `pages/` ou `views/`: Login, Dashboard, Generator, Results, Admin
   - `components/`: Button, Modal, Pagination, Toggle, Toast
   - `services/`: API client, Auth context

3. Definir contratos de API (consumo dos endpoints existentes).

4. Definir estratégia de SSR/SSG/CSR.

### Critério de aceite
- `specs/020-web-frontend/spec.md` completo
- Contratos de API mapeados contra backend existente

---

## A04 — Criar Spec 021 — Mobile App (P1)

**Problema**: Constitution VII (v1.2.0) exige Android + iOS. Nenhuma spec
existe.

**Complexidade**: ALTA  
**Tempo estimado**: 2h  
**Arquivos a criar**: `specs/021-mobile-app/spec.md`, `specs/021-mobile-app/checklists/requirements.md`

### Passos

1. Executar `/speckit.specify` com descrição baseada na Constitution VII:
   - Android (Kotlin/Compose ou React Native) e iOS (Swift/SwiftUI ou React Native)
   - Funcionalidades equivalentes ao web frontend
   - Suporte offline parcial (cache local de combinações)
   - Push notifications para resultados

2. Incluir seção de benchmark: versões mínimas de SO a definir após
   análise de mercado.

3. Definir estratégia de compartilhamento de código (React Native vs nativo).

### Critério de aceite
- `specs/021-mobile-app/spec.md` completo
- Definição clara de versões mínimas (mesmo que postergada)

---

## A05 — Atualizar Constitution Technical Constraints (P1)

**Problema**: Constitution ainda referencia tabela `sorteios_historicos`
(genérica) enquanto os coletores usam `loterias_resultados_{jogo}`.

**Complexidade**: BAIXA  
**Tempo estimado**: 15 min  
**Arquivos afetados**: `.specify/memory/constitution.md`

### Passos

1. Localizar seção "Technical Constraints" > "Database".

2. Substituir:
   ```diff
   - Tabela `sorteios_historicos`: imutável, com hash único...
   + Tabelas `loterias_resultados_{jogo}`: uma por jogo (10 no total),
   + cada uma imutável, com hash único SHA-256 da combinação...
   ```

3. Adicionar nota sobre exceção da Federal (usa `Extração` como PK).

### Critério de aceite
- Constitution não contém mais referências a `sorteios_historicos`
- `loterias_resultados_*` documentado como padrão

---

## A06 — Atualizar Plan com Cobertura Total de Specs (P1)

**Problema**: Plan v0.1-beta cita specs 001–006 e menciona coletores 007–017
mas não reflete as inconsistências descobertas nem as 3 novas specs
pendentes (019, 020, 021).

**Complexidade**: MÉDIA  
**Tempo estimado**: 45 min  
**Arquivos afetados**: `.plan/v0.1-beta-plan.md`

### Passos

1. Adicionar **Fase 0.5 — Correções** entre Fase 0 e Fase 1:
   - Recuperação dos FRs 001–027 na spec 004
   - Criação das specs faltantes (019, 020, 021)

2. Adicionar **Fase 4 — Frontend & Mobile** (semana 11–12):
   - Implementação do web frontend (React/Next.js ou Vue.js)
   - Implementação do mobile app (Android + iOS)

3. Atualizar **Technical Context**:
   - Adicionar frontend: React/Next.js ou Vue.js + Vite
   - Adicionar mobile: React Native ou Kotlin/Swift (TBD)

4. Atualizar **Success Criteria** com:
   - Export funcionando em 3 formatos (CSV, JSON, PDF)
   - Web frontend responsivo com todas as telas
   - Mobile app compilando para Android e iOS

### Critério de aceite
- Plan lista todas as 20+ specs planejadas
- Fases refletem a ordem correta de dependências

---

## A07 — Unificar Definição de `feature_toggles` (P2)

**Problema**: `feature_toggles` definido em spec 002 (FR-001) e spec 003
(entidades), sem referência cruzada.

**Complexidade**: BAIXA  
**Tempo estimado**: 15 min  
**Arquivos afetados**: `specs/003-system-management/spec.md`

### Passos

1. Em spec 003, seção "Key Entities", substituir a redefinição de
   `FeatureToggle` por:
   ```markdown
   - **FeatureToggle**: (mesma entidade da Spec 002 — ver definição
     completa em `specs/002-modular-feature-system/spec.md`)
   ```

2. Adicionar nota: "Este spec NÃO redefine a entidade — apenas referencia."

### Critério de aceite
- Spec 003 não contém definição duplicada de `feature_toggles`
- Referência cruzada explícita para spec 002

---

## A08 — Definir Tabela `combinacoes_salvas` (P2)

**Problema**: Tabela referenciada mas sem definição de colunas em spec alguma.

**Complexidade**: BAIXA  
**Tempo estimado**: 15 min  
**Arquivos afetados**: `specs/001-bet-simulation-promise/spec.md`

### Passos

1. Em spec 001, seção "Key Entities", adicionar:
   ```markdown
   - **CombinacaoSalva**: Representa uma combinação salva pelo usuário.
     Atributos: `id` (UUID), `user_id` (FK → users), `jogo` (VARCHAR 50),
     `dezenas` (INTEGER[]), `dezenas_por_aposta` (INTEGER),
     `favorita` (BOOLEAN), `created_at` (TIMESTAMPTZ).
     Limite: 200 por usuário. FIFO com proteção de favoritos.
   ```

2. Referenciar que a DDL completa está na spec 004 (após restauração dos FRs).

### Critério de aceite
- Spec 001 contém definição clara da entidade

---

## A09 — Documentar Estratégia de Nomeação de Colunas (P2)

**Problema**: Tabelas `loterias_resultados_*` usam colunas com espaços e
acentos, exigindo quoting no SQL. Decisão não documentada.

**Complexidade**: BAIXA  
**Tempo estimado**: 10 min  
**Arquivos afetados**: `specs/004-database-architecture/spec.md`

### Passos

1. Adicionar seção "Naming Convention" em spec 004:
   ```
   ## Naming Convention para loterias_resultados_*
   
   As colunas das tabelas `loterias_resultados_{jogo}` usam EXATAMENTE
   os mesmos nomes dos cabeçalhos da planilha oficial da CEF, incluindo
   espaços, acentos e caracteres especiais (ex: "Data do Sorteio",
   "Ganhadores 6 acertos", "1º prêmio"). Isso garante que:
   
   1. O parse com Polars pode mapear colunas diretamente sem transformação
   2. A depuração é facilitada (consulta SQL vs. planilha são idênticas)
   3. Mudanças na planilha CEF são detectadas por diferença de cabeçalho
   
   Consequência: todo SQL contra estas tabelas DEVE usar aspas duplas.
   Exemplo: SELECT "Concurso", "Data do Sorteio" FROM loterias_resultados_megasena
   ```

### Critério de aceite
- Decisão documentada e rastreável

---

## A10 — Especificar Mecanismo de Sessão Anônima + Redis (P2)

**Problema**: Constitution II exige Redis para sessões anônimas mas
nenhuma spec detalha a integração.

**Complexidade**: MÉDIA  
**Tempo estimado**: 30 min  
**Arquivos afetados**: `specs/003-system-management/spec.md` (seção assumptions)
ou novo task no plan

### Passos

1. Documentar em spec 003 (assumptions):
   ```markdown
   - **Sessão anônima**: Usuários não autenticados recebem um `session_id`
     armazenado em Redis com TTL de 30 dias. O `session_id` é gerado como
     UUID v4 e enviado via cookie `session_id` (HttpOnly, Secure, SameSite=Lax).
   - **Redis**: Usado como session store. TTL configurável via env var
     `SESSION_TTL_SECONDS` (default 2.592.000 = 30 dias).
   ```

2. Adicionar task no plan para implementar middleware de sessão anônima.

### Critério de aceite
- Mecanismo de sessão anônima documentado
- TTL e cookie config explicitados

---

## Resumo

| ID | Ação | Prioridade | Complexidade | Tempo | Afeta |
|---|---|---|---|---|---|
| A01 | Recuperar FR-001 a 027 na spec 004 | **P0** | Baixa | 30 min | spec 004 |
| A02 | Criar spec 019 — Export & Share | **P0** | Média | 1h | Novo spec |
| A03 | Criar spec 020 — Web Frontend | **P0** | Alta | 2h | Novo spec |
| A04 | Criar spec 021 — Mobile App | **P1** | Alta | 2h | Novo spec |
| A05 | Atualizar Constitution DB constraints | **P1** | Baixa | 15 min | Constitution |
| A06 | Atualizar Plan com cobertura total | **P1** | Média | 45 min | Plan |
| A07 | Unificar `feature_toggles` | **P2** | Baixa | 15 min | spec 003 |
| A08 | Definir `combinacoes_salvas` | **P2** | Baixa | 15 min | spec 001 |
| A09 | Documentar naming convention | **P2** | Baixa | 10 min | spec 004 |
| A10 | Especificar Redis/sessão anônima | **P2** | Média | 30 min | spec 003 |

**Total**: 10 ações | **Tempo total estimado**: ~7h

### Sequência sugerida

```
A01 ──→ A05 ──→ A06 ──→ A07 ──→ A08 ──→ A09 ──→ A10
  │
  ├── A02 (paralelo, depende de nenhum)
  ├── A03 (paralelo, depende de nenhum)
  └── A04 (paralelo, depende de A03 — mobile compartilha contratos com web)
```

**Ordem de execução recomendada**:
1. **A01** (recuperar FRs perdidos — desbloqueia dependências)
2. **A02** + **A03** em paralelo (criação de specs críticas ausentes)
3. **A05** + **A06** em paralelo (alinhar Constitution e Plan)
4. **A07** + **A08** + **A09** + **A10** em paralelo (ajustes finos)
5. **A04** (mobile app — depende dos contratos definidos em A03)
