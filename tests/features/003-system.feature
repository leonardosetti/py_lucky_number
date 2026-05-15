Feature: System Management (Auth, Roles, Users)
  Como um administrador
  Quero gerenciar usuários, roles e permissões
  Para controlar acesso ao sistema

  Background:
Given que existem 4 roles no sistema: Admin, Auditor, TestDemo, Apostador

  Scenario: Registrar novo usuário
Given que um novo usuário acessa a página de registro
When ele preenche email "novo@email.com" e senha "Str0ng!Pass"
Then a conta é criada com role Apostador
And a senha é armazenada como bcrypt hash (custo 12)

  Scenario: Login com credenciais válidas
Given que o usuário "maria@email.com" possui conta
When ele faz login com email e senha corretos
Then um JWT é retornado
And o token contém user_id e role

  Scenario: Login com senha inválida
Given que o usuário "maria@email.com" possui conta
When ele faz login com senha incorreta
Then o sistema retorna 401 Unauthorized
And o evento é registrado no audit_log

  Scenario: Bloquear exclusão do último admin
Given que existe apenas 1 usuário com role Admin
When uma tentativa de excluir este usuário é feita
Then o sistema bloqueia com erro "Não é possível excluir o último administrador"

  Scenario: Bloquear auto-exclusão
Given que o admin está autenticado
When ele tenta excluir a própria conta
Then o sistema bloqueia com erro "Você não pode excluir sua própria conta"

  Scenario: Auditor tem acesso somente leitura
Given que o usuário "auditor@email.com" está autenticado com role Auditor
When ele tenta criar um novo usuário via POST /api/v1/admin/users
Then o sistema retorna 403 Forbidden

  Scenario: TestDemo com transaction rollback
Given que o usuário "teste@email.com" está autenticado com role TestDemo
When ele cria, edita ou exclui entidades
Then as operações são executadas durante a sessão
When a sessão termina (logout ou timeout 8h)
Then todas as alterações são revertidas (transaction rollback)

  Scenario: Rate limiting em operações admin
Given que um admin autenticado
When ele faz 31 requisições em 1 minuto
Then a 31ª requisição retorna 429 Too Many Requests

  Scenario: Exclusão de usuário com confirmação em 2 passos
Given que o admin seleciona um usuário para excluir
When ele clica em "Excluir"
Then uma mensagem de confirmação é exibida: "Tem certeza?"
When ele confirma o primeiro passo
Then uma segunda confirmação é exibida: "Esta ação é irreversível"
When ele confirma o segundo passo
Then o usuário é marcado como inativo (soft delete)
And o evento é registrado no audit_log
