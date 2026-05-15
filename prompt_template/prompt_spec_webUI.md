# Web + UI/UX + Data — Spec Guide

Este documento organiza as diretivas de geração de código para o Lucky Number
em 3 blocos (Code, UI/UX, Data), cada um com seções para Web e Mobile.
Aderente à Constitution v1.4.0 (CWE Top 25, Python/Go idioms, Data Security).

A stack de frontend é **agnóstica à linguagem**: a escolha deve recair sobre
a opção mais segura e performática segundo os preceitos da Constitution.
Opções recomendadas: React + Next.js ou Vue.js + Vite/PWA (web);
React Native, Kotlin/Compose ou Swift/SwiftUI (mobile).

---

## Bloco 1 — Code

### 1.1 Web Implementation

#### Priority Order (5 níveis)
1. Security & CWE Compliance — evitar CWE Top 25 (2024). Sem exceções.
2. Testabilidade — código testável isoladamente.
3. Language-specific secure idioms — seguir PEPs/TC39 proposals estágio 2+.
4. Functional correctness — respeitar spec/plan exatamente.
5. Readability — nomes significativos, comentários apenas para lógica não óbvia
   ou segurança/testabilidade.

#### CWE Top 25 (2024) — Obrigatório
Para cada bloco de código, gerar comentário indicando qual CWE está sendo
mitigada:

| CWE | Nome | Mitigação Web |
|-----|------|---------------|
| 89 | SQL Injection | Parameterized query via asyncpg. Proibida concatenação. |
| 79 | XSS | Output encoding contextual. React: `{data}` escapa automaticamente. |
| 352 | CSRF | Token anti-CSRF em mutações via API. |
| 20 | Input Validation | Pydantic no backend + validação client-side apenas para UX. |
| 522 | Credential Protection | bcrypt custo 12. JWT em HttpOnly cookies. Nunca hardcoded. |
| 918 | SSRF | Validar e allowlistar URLs de download (coletores CEF). |
| 502 | Deserialization | Usar Pydantic/orjson. Nunca `pickle` ou `eval`. |
| 434 | File Upload | Validar extensão/MIME + ClamAV. |
| 22 | Path Traversal | Nunca usar input do usuário para paths de arquivo. |
| 78 | OS Command Injection | Evitar `os.system()`. Usar `subprocess` com lista de args. |
| 778/779 | Logging | Logs JSON sem secrets. Auditoria imutável. |
| 284 | Access Control | JWT + RBAC + RLS no PostgreSQL. |

Referência: https://cwe.mitre.org/top25/

#### Python (Backend) — Padrões Obrigatórios
- PEP 8, line length ≤ 88. Black + isort + ruff.
- Type hints obrigatórios em funções públicas.
- Async/await para I/O (FastAPI, HTTPX, asyncpg).
- Secrets via variáveis de ambiente (pydantic-settings). Nunca hardcoded.
- Arquivos temporários: usar `tempfile` module (previne CWE-379).
- Exemplo de resposta obrigatória:
  ```python
  async def fetch_user(user_id: int, db: asyncpg.Connection):
      # Prevents CWE-89: SQL injection via parameterized query
      row = await db.fetchrow(
          "SELECT id, name, email FROM users WHERE id = $1", user_id
      )
      return row
  ```

#### JavaScript/TypeScript (Frontend Web) — Padrões Obrigatórios
- TC39 estágio 2+ permitido se melhorar segurança/clareza.
- camelCase para variáveis/funções. PascalCase para componentes.
- UPPER_SNAKE_CASE para constantes.
- Nunca usar `innerHTML` — usar `textContent` ou React `{data}` (previne CWE-79).
- fetch/axios com timeout configurado. Tratar erros 4xx/5xx genericamente.
- Exemplo de resposta obrigatória:
  ```typescript
  // Prevents CWE-79: XSS via React's automatic escaping
  // Prevents CWE-352: CSRF token included in mutation headers
  async function submitBet(betData: BetRequest, csrfToken: string): Promise<BetResponse> {
    const res = await fetch("/api/v1/gerar-apostas", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify(betData),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }
  ```

### 1.2 Mobile Implementation

#### Swift (iOS) — Padrões Obrigatórios
- Swift Evolution Proposals (SE) estágio recomendado como referência.
- Evitar CWE-200 (Information Exposure): não logar dados do usuário.
- Evitar CWE-732 (Incorrect Permissions): usar entitlement mínimos.
- URLSession com certificate pinning para chamadas à API.
- Keychain para armazenar tokens JWT. Nunca UserDefaults.
- Exemplo:
  ```swift
  // Prevents CWE-200: token stored in Keychain, not UserDefaults
  // Prevents CWE-89: API parameterized on server side
  func fetchBets() async throws -> [Bet] {
      let token = try await Keychain.shared.get("jwt")
      var request = URLRequest(url: URL(string: "\(baseURL)/api/v1/promessas")!)
      request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
      let (data, _) = try await URLSession.shared.data(for: request)
      return try JSONDecoder().decode([Bet].self, from: data)
  }
  ```

#### Kotlin (Android) — Padrões Obrigatórios
- KEEP (Kotlin Evolution) como referência.
- Coroutines para async. Retrofit + OkHttp para API calls.
- EncryptedSharedPreferences ou Android Keystore para tokens.
- ProGuard/R8 para ofuscar o binário release.
- Evitar CWE-200: não logar dados sensíveis. Usar `Log.d` apenas em debug.
- Exemplo:
  ```kotlin
  // Prevents CWE-522: token in EncryptedSharedPreferences
  // Prevents CWE-89: parameterized on server
  interface LuckyApi {
      @POST("api/v1/gerar-apostas")
      suspend fun gerarApostas(
          @Header("X-CSRF-Token") csrf: String,
          @Body request: ApostaRequest
      ): ApostaResponse
  }
  ```

#### React Native (Cross-Platform) — Padrões Obrigatórios
- AsyncStorage criptografado para tokens (ex: react-native-encrypted-storage).
- fetch nativo com certificados fixos ou SSL pinning.
- Código compartilhado entre iOS/Android deve evitar plataforma-specific APIs.
- Exemplo:
  ```typescript
  // Prevents CWE-522: token in encrypted storage
  const token = await EncryptedStorage.get("jwt");
  const response = await fetch(`${API_URL}/promessas`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  ```

---

## Bloco 2 — UI/UX

### 2.1 Web Implementation

#### Priority Order
1. Accessibility — WCAG 2.2 AA minimum.
2. Testability & QA Automation — data-testid em todo elemento interativo.
3. Security in UI — OWASP + CWE mitigations.
4. Retention & Engagement — Hooked Model, onboarding, metrics.
5. Responsive & Cross-Browser — mobile-first, viewport coverage.
6. Usability Heuristics — Nielsen, Hick, Fitts, Doherty Threshold.

#### Accessibility (WCAG 2.2 AA)
- ARIA labels em todos os inputs e botões sem texto visível.
- Gerenciamento de foco em modais e navegação por teclado.
- Contraste mínimo 4.5:1 (texto normal), 3:1 (texto grande).
- Suporte a leitores de tela: `role`, `aria-live`, `aria-describedby`.
- Gerar scripts de teste: axe-core, Lighthouse CI, pa11y.
- Exemplo:
  ```tsx
  <input
    id="email"
    type="email"
    aria-label="Email address"
    data-testid="email-input"
  />
  ```

#### Testability & QA Automation
- Todo elemento interativo DEVE ter `data-testid` único e estável.
- Formato: `data-testid="{component}-{action}-{state}"`.
- Listas dinâmicas: `data-testid="{item-type}-{entity-id}-{action}"` (id estável,
  não índice de array).
- Estados de loading: `data-testid="loading-spinner"` ou `"{component}-loading"`.
- Mensagens de erro: `data-testid="error-{context}"` (ex: `error-login`).
- Inputs: `data-testid` deve bater com o nome do campo (`email-input`).
- Elementos condicionais: testid deve aparecer no DOM junto com o elemento.
- Nunca depender de seletores auto-gerados pelo framework (Vue `data-v-*`,
  React internal IDs, Angular `_ngcontent-*`).
- Comentário obrigatório: `// data-testid for QA: login-submit-button`.
- Suportar paralelismo: componentes stateless, sem mutáveis globais.
- Testar com Playwright ou Cypress usando `data-testid` como seletor único.

#### Security in UI
- Nunca expor IDs de usuário em data-testid (usar tokens estáveis).
- CSRF token em toda mutação (CWE-352).
-Timeout de sessão configurável (CWE-613).
- Logout forçado após inatividade.
- Exemplo:
  ```tsx
  // Prevents CWE-352: CSRF token in header
  // Prevents CWE-200: no user PII in data-testid
  <button
    onClick={() => handleDelete(promiseId)}
    data-testid={`promessa-${promiseId}-delete`}
    aria-label="Excluir promessa"
  >
    Excluir
  </button>
  ```

#### Responsive & Cross-Browser
- Mobile-first com `min-width` media queries.
- Breakpoints: 320px (mobile), 768px (tablet), 1024px (desktop), 1440px (wide).
- Touch targets: mínimo 44x44pt (Apple) ou 48x48px (Material).
- Viewports: iPhone SE (375x667), iPhone 12/13/14 (390x844), Pixel 5 (393x851),
  iPad (768x1024), Desktop 1280x720 e 1920x1080.
- Unidades relativas: `rem`, `em`, `vh`, `vw`, `%`, `clamp()`.
- CSS Grid, Flexbox, container queries. Proibido float/table layouts.
- Navegadores: últimas 2 versões de Chrome, Firefox, Safari, Edge. Sem IE11.
- Layout responsivo e componentes:
  ```tsx
  // Mobile-first: data-testid presente em todas as resoluções
  <div className={styles.grid} data-testid="results-grid">
    {items.map(item => (
      <Card key={item.id} data-testid={`result-card-${item.id}`} />
    ))}
  </div>
  ```
  ```css
  .grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  @media (min-width: 768px) {
    .grid { grid-template-columns: repeat(2, 1fr); }
  }
  @media (min-width: 1024px) {
    .grid { grid-template-columns: repeat(3, 1fr); }
  }
  ```

#### Frameworks Permitidos (Web)
React, Vue, Svelte, Angular, Lit, Solid, Preact — com as constraints:
- Deve permitir `data-testid` como atributo padrão no DOM.
- SSR (Next.js, Nuxt, SvelteKit, Astro): testids devem sobreviver à hidratação.
- CSS pode ser CSS Modules, Styled Components, Tailwind, ou CSS puro.
- A escolha deve priorizar segurança e performance conforme Constitution.

#### UX Laws & Heuristics
- Nielsen: visibilidade do status do sistema, consistência, prevenção de erros.
- Hick: reduzir opções por tela, agrupar por prioridade.
- Fitts: botões de ação primária maiores e próximos.
- Doherty Threshold: feedback em <400ms para operações comuns.
- Von Restorff: destacar ação principal (call to action).

### 2.2 Mobile Implementation

#### Platform Conventions
- iOS: seguir Apple Human Interface Guidelines.
- Android: seguir Material Design 3 (Material You).
- React Native: aderir à plataforma alvo automaticamente ou via biblioteca
  (ex: React Native Paper para Material, NativeBase para cross).

#### Touch & Gestures
- Touch targets mínimos: 48x48dp (Material), 44x44pt (iOS).
- Swipe para excluir suportado (Constitution VII).
- Haptic feedback opcional para ações destrutivas.
- Evitar gestos que conflitem com navegação nativa (ex: swipe back).

#### Navigation Patterns
- Mobile: Bottom Tab Navigation (Constitution VII).
- Drawer lateral opcional para tablets em landscape.
- Deep linking para compartilhamento de promessas (spec 001/019).
- Exemplo:
  ```kotlin
  // Bottom nav com data-testid (convertido para resource por QA)
  @Composable
  fun BottomNavBar(onNavigate: (Route) -> Unit) {
      BottomNavigation(modifier = Modifier.semantics { testTag = "bottom-nav" }) {
          BottomNavigationItem(
              icon = { Icon(Icons.Default.Home, contentDescription = "Início") },
              selected = true,
              onClick = { onNavigate(Route.Home) },
              modifier = Modifier.semantics { testTag = "nav-home" }
          )
      }
  }
  ```

#### Biometrics & Security
- Biometria (Face ID / Touch ID / fingerprint) opcional para login.
- Keychain (iOS) / Keystore (Android) para tokens — nunca SharedPreferences.
- Session timeout igual ao web (30 dias para anônimos, configurável).

---

## Bloco 3 — Data

### 3.1 Web Implementation

#### API Contracts (REST)
- FastAPI + Pydantic v2 para validação automática (previne CWE-20).
- Todos os endpoints retornam JSON. Nunca HTML.
- Respostas de erro padronizadas: `{ "detail": string, "status_code": int }`.
- Exemplo obrigatório:
  ```python
  from pydantic import BaseModel, Field
  
  class ApostaRequest(BaseModel):
      jogo: str = Field(..., min_length=1)
      quantidade_apostas: int = Field(ge=1, le=10)  # Prevines invalid range
      dezenas_por_aposta: int = Field(ge=6, le=20)
  
  @router.post("/gerar-apostas")
  async def gerar_apostas(req: ApostaRequest):
      # Prevents CWE-20: input validated by Pydantic
      # Prevents CWE-89: parameterized query via asyncpg
      ...
  ```

#### Caching Strategy
- Redis para feature flags (TTL 60s).
- Redis para sessões anônimas (TTL 30 dias).
- Browser cache: `Cache-Control: no-store` para dados sensíveis.
- Service Worker (PWA) para cache offline de resultados estáticos.

#### Database Access
- asyncpg com parameterized queries (previne CWE-89).
- SQLAlchemy 2.0 Core + Alembic para migrações.
- Row-level security para isolar dados de usuários (CWE-284).
- Exemplo:
  ```python
  # Prevents CWE-89: parameterized query
  # Prevents CWE-284: RLS on table
  await db.execute(
      "INSERT INTO combinacoes_salvas (user_id, jogo, dezenas, hash_combinacao) VALUES ($1, $2, $3, $4)",
      user_id, jogo, dezenas, hash_combinacao
  )
  ```

### 3.2 Mobile Implementation

#### Offline Storage
- SQLite (via WCDB/GRDB iOS, Room Android, ou expo-sqlite RN) para cache local.
- Espelhar o schema do backend apenas para leitura (tabelas de resultados).
- Queue de operações offline: sincronizar quando online (reconciliation).
- Exemplo (Kotlin/Room):
  ```kotlin
  @Entity(tableName = "combinacoes_cache")
  data class CombinacaoCache(
      @PrimaryKey val id: String,
      val jogo: String,
      val dezenas: String,  // JSON array
      val hash: String,
      val created_at: Long
  )
  ```

#### Sync Strategy
- Ao voltar online: sincronizar operações pendentes (FIFO).
- Conflitos: "last write wins" para dados não críticos; "manual resolution"
  para promessas.
- Cache de resultados de sorteio: invalidar a cada 6h (mesmo schedule dos coletores).

#### Data Security (Mobile)
- Criptografar banco SQLite com SQLCipher ou biblioteca equivalente.
- Keychain (iOS) / EncryptedSharedPreferences (Android) para tokens.
- Cache em memória zerado ao entrar em background (previne CWE-200).
- Exemplo (Swift/SQLCipher):
  ```swift
  // Prevents CWE-522: encrypted database
  var db = try DatabaseQueue()
  try db.key(try Keychain.shared.get("db_key"))
  try db.read { db in
      let rows = try Row.fetchAll(db, sql: "SELECT * FROM combinacoes_cache WHERE user_id = ?", arguments: [userId])
  }
  ```
