Feature: Backup Automation
  Como um administrador
  Quero garantir que backups do banco sejam executados e validados
  Para recuperar o sistema em caso de desastre

  Scenario: Backup completo programado
Given que o scheduler está configurado para 03:00 UTC
When o horário agendado é atingido
Then pgBackRest executa backup full com criptografia AES-256-GCM
And o backup é verificado (checksum SHA-256)
And o resultado é registrado em backup_history

  Scenario: Restore com --force em produção
Given que um arquivo de backup válido existe
When o admin executa restore sem a flag --force
Then o sistema bloqueia com erro "Use --force para restore em produção"
When o admin executa com --force
Then o restore é executado e validado

  Scenario: Falha no download com retry
Given que a URL de download da CEF está fora do ar
When o coletor de backup tenta baixar
Then o sistema faz retry com backoff exponencial (até 3 tentativas)
And após 3 falhas, uma notificação admin é criada

  Scenario: Lockfile impede execução concorrente
Given que um backup está em execução
When o scheduler tenta iniciar outro backup
Then o sistema detecta o lockfile em /var/lock/backup.lock
And registra "Backup já em execução" no log
