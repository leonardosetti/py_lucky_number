# Lucky Number — TODOs do Projeto

> Arquivo central de acompanhamento de tarefas pendentes, especificações não geradas e
> inconsistências identificadas nas análises de consistência entre artefatos (Constitution,
> Specs, Plan). Atualizado em: 2026-05-14.

---

## Legenda

| Marcação | Significado |
|---|---|
| 🔴 CRITICAL | Viola Constitution ou bloqueia funcionalidade baseline |
| 🟠 HIGH | Impacta qualidade, segurança ou integridade |
| 🟡 MEDIUM | Melhoria necessária, não bloqueante |
| 🟢 LOW | Refinamento opcional |

---

## 1. Specs Não Geradas (Missing Specs)

### 🔴 [019] Export & Share — CSV, JSON, PDF, WhatsApp

**Motivação**: Constitution Princípio VI exige exportação de combinações nos formatos
CSV, JSON, PDF e compartilhamento via WhatsApp (`wa.me`), e-mail entre usuários
registrados e cópia para área de transferência. Funcionalidade completamente ausente.

**Escopo mínimo esperado**:
- [ ] Endpoint `GET /api/v1/export/csv` — exportar combinações em CSV
- [ ] Endpoint `GET /api/v1/export/json` — exportar combinações em JSON
- [ ] Endpoint `GET /api/v1/export/pdf` — exportar combinações em PDF
- [ ] Geração de link `wa.me` com mensagem pré-formatada
- [ ] Compartilhamento entre usuários registrados (envio por ID interno)
- [ ] Cópia para área de transferência (suporte via API)
- [ ] Controle de acesso: próprio usuário exporta apenas suas combinações

---

### 🔴 [020] Web Frontend — Interface Web Responsiva

**Motivação**: Constitution Princípio VII exige aplicação web responsiva (mobile-first)
com React/Next.js ou Vue.js/PWA. Atualmente o projeto possui apenas backend.
Interface atual é JSON puro + rota `/` com FileResponse.

**Escopo mínimo esperado**:
- [ ] Escolha do framework (React + Next.js ou Vue.js + Vite/PWA)
- [ ] Tela de login/registro
- [ ] Tela de geração de apostas (seleção de jogo, quantidade, dezenas)
- [ ] Tela de resultados (combinações salvas, promessas)
- [ ] Painel admin (features, usuários, notificações, dashboard)
- [ ] Design responsivo (mobile-first)
- [ ] Tema claro/escuro
- [ ] Paginação (20 itens/página)
- [ ] Suporte a acessibilidade (WCAG 2.1 AA)

---

### 🔴 [021] Mobile App — Android e iOS

**Motivação**: Constitution Princípio VII (v1.2.0) determina que o software deve ser
implementado tanto como web-based app quanto como mobile app nativo para Android e
iOS.

**Escopo mínimo esperado**:
- [ ] Benchmark e análise de mercado para definir versões mínimas suportadas
- [ ] Definição da estratégia: React Native (compartilha código com web) vs Kotlin/Compose
      + Swift/SwiftUI
- [ ] Funcionalidades equivalentes ao web frontend
- [ ] Suporte offline parcial (combinações salvas em cache local)
- [ ] Push notifications para resultados de sorteios

---

## 2. Inconsistências e Correções em Specs Existentes

### 🔴 Spec 004 — FRs 001–027 Perdidos na Substituição v2.0

**Problema**: A spec 004 foi substituída pela v2.0 (018→004), mas o novo arquivo
contém apenas FR-028 a 035 (5 novas tabelas). Os FRs originais 001–027 (ambientes,
migrações, constraints, segurança, OWASP/CWE) foram perdidos.

**Ação**: Reincorporar FR-001 a 027 da spec 004 original ao arquivo atual, mantendo
FR-028 a 035 como extensão.

- [ ] Restaurar FR-001 a 004 (database environments)
- [ ] Restaurar FR-005 a 008 (schema & migrations)
- [ ] Restaurar FR-009 a 014 (data integrity & constraints)
- [ ] Restaurar FR-015 a 023 (security & compliance)
- [ ] Restaurar FR-024 a 027 (containerization & CI/CD)
- [ ] Verificar numeração final (deve ser FR-001 a FR-035 sequencial)

### 🟠 Constitution Technical Constraints — `sorteios_historicos` vs `loterias_resultados_*`

**Problema**: Constitution ainda referencia tabela genérica `sorteios_historicos`,
mas os coletores (specs 007–017) usam `loterias_resultados_{jogo}` (uma por jogo).
As duas abordagens são mutuamente exclusivas e conflitam.

**Ação**: Atualizar seção "Technical Constraints" na Constitution para refletir
o schema real.

- [ ] Substituir `sorteios_historicos` por `loterias_resultados_{jogo}` (10 tabelas)
- [ ] Adicionar nota sobre `Extração` como PK alternativa para Federal
- [ ] Remover referência obsoleta a tabela única de histórico

### 🟡 Spec 002/003 — `feature_toggles` Duplicado

**Problema**: Entidade `feature_toggles` definida em spec 002 (FR-001) e spec 003
(entidades), sem referência cruzada. Risco de divergência futura.

**Ação**:
- [ ] Spec 002: definição canônica da tabela `feature_toggles`
- [ ] Spec 003: referenciar spec 002 em vez de redefinir

### 🟡 Spec 001 — `combinacoes_salvas` Sem Definição

**Problema**: Tabela `combinacoes_salvas` é referenciada em spec 001 e no schema
original da spec 004, mas a spec 004 atual (v2.0) não a define. A tabela não tem
definição de colunas em spec alguma.

**Ação**:
- [ ] Adicionar definição da tabela em spec 001 ou restaurar em spec 004
- [ ] Definir colunas: id, user_id, jogo, dezenas, dezenas_por_aposta, favorita,
      created_at, limit 200/user, FIFO policy

### 🟡 Spec 004 — Colunas com Espaços/Acentos

**Problema**: Tabelas `loterias_resultados_*` usam nomes de colunas com espaços e
acentos (ex: `"Data do Sorteio"`, `"Ganhadores 6 acertos"`, `"1º prêmio"`),
exigindo quoting constante em SQL.

**Decisão pendente**: Manter fiel à planilha (com quoting) ou normalizar para
`snake_case` (ex: `data_sorteio`, `ganhadores_6_acertos`)?
- [ ] Documentar decisão na spec 004
- [ ] Se normalizar, criar mapeamento planilha → coluna em cada collector

---

## 3. Funcionalidades Subespecificadas

### 🟡 Spec 003 — Georreferenciamento (FR-022)

**Problema**: FR-022 exige filtro por "região geográfica" no dashboard, mas
nenhum mecanismo de geolocalização (GeoIP, GPS, cadastro explícito) é definido
em spec alguma. Assumption em spec 003 diz "região inferida do IP".

**Ação**:
- [ ] Criar tarefa de implementação para GeoIP (MaxMind ou similar)
- [ ] Definir tabela de fallback (região não identificada)
- [ ] Especificar middleware de captura de `ip_hash` + `regiao`

### 🟡 Redis para Sessões Anônimas

**Problema**: Constitution II determina Redis para sessões anônimas
(combinações efêmeras). Nenhuma spec cobre a integração Redis + sessão.

**Ação**:
- [ ] Especificar integração Redis no plano de implementação
- [ ] Definir TTL de sessão anônima (default 30 dias conforme spec 001)
- [ ] Mapear entidades que usam `session_id` (promessas, usage_events)

---

## 4. Melhorias no Plan

### 🟢 Atualizar Plan com Cobertura de Todas as Specs

- [ ] Plan atual referencia specs 001–006 e 007–017 mas não menciona spec 004 v2
- [ ] Adicionar fase específica para specs 019 (Export), 020 (Web), 021 (Mobile)
- [ ] Detalhar stack frontend e mobile no Technical Context

---

## 5. Tarefas que Requerem Nova API no Backend

### 🟡 T157 — Página de Perfil (Profile)

**Problema**: A página de perfil (alterar senha, excluir conta - LGPD) requer
endpoints de API que não existem no backend:
- `PUT /api/v1/auth/password` — alterar senha (bcrypt)
- `DELETE /api/v1/auth/account` — excluir conta (soft delete + anonimização LGPD)

**Ação necessária**:
1. Criar `PUT /api/v1/auth/password` em `src/lucky_number/api/routes.py`
   - Receber: `current_password`, `new_password`
   - Validar senha atual, atualizar hash
2. Criar `DELETE /api/v1/auth/account` em `src/lucky_number/api/routes.py`
   - Soft delete (ativo=false, deleted_at=now)
   - Anonimizar dados pessoais (nome → "Usuário removido", email → hash)
3. Criar página Perfil em `web/src/app/profile/page.tsx`
   - Formulário de alteração de senha
   - Botão "Excluir Conta" com confirmação em 2 passos

---

## Resumo

| Tipo | Quantidade |
|---|---|
| 🔴 Specs faltantes (CRITICAL) | 3 |
| 🔴 Inconsistências em specs existentes | 2 |
| 🟠 Inconsistências Constitution vs Specs | 1 |
| 🟡 Melhorias em specs / APIs faltantes | 5 |
| 🟢 Ajustes no Plan | 1 |

**Total de TODOs**: 29 itens (entre abertos e fechados)
