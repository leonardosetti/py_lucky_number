Feature: Environment Management
  Como um desenvolvedor
  Quero ambientes isolados com branches específicas
  Para desenvolver sem afetar produção

  Scenario: Gitflow com branches protegidas
Given que o repositório segue gitflow
When um desenvolvedor cria feature/nova-funcionalidade a partir de develop
Then a branch contém o código base + alterações da feature
And não impacta develop ou main

  Scenario: Deploy em produção requer aprovação manual
Given que um merge para main foi concluído
When a pipeline de CD é acionada
Then ela pausa e exige aprovação manual
And executa rolling update com health check

  Scenario: Ambiente demo com dados sintéticos
Given que o ambiente demo está configurado
When um stakeholder acessa a URL
Then o sistema está funcional com dados sintéticos
And nenhum dado real de produção está presente
And as alterações são efêmeras (reset diário)
