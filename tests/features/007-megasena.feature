Feature: Mega-Sena Data Collector
  Como o sistema
  Quero coletar sorteios da Mega-Sena da CEF
  Para manter a base histórica atualizada

  Background:
Given que a URL da planilha é https://servicebus3.caixa.gov.br/.../Mega-Sena

  Scenario: Carga inicial na primeira execução
Given que o arquivo ./data/megasena.json não existe
When o coletor executa
Then a planilha é baixada e parseada com Polars
And o JSON é criado com todos os sorteios
And a tabela loterias_resultados_megasena é populada

  Scenario: Atualização incremental sem novos concursos
Given que o último concurso no JSON é 2800
When o scheduler executa e a planilha contém até 2800
Then nenhum novo registro é adicionado
And o JSON e o banco não são alterados

  Scenario: Atualização incremental com novos concursos
Given que o último concurso no JSON é 2800
When o scheduler executa e a planilha contém até 2802
Then apenas os concursos 2801 e 2802 são adicionados
And o JSON é reescrito com os novos registros

  Scenario: Falha no download preserva dados existentes
Given que a URL da CEF retorna HTTP 500
When o coletor tenta baixar
Then o erro é registrado no log
And os dados anteriores permanecem intactos
And o arquivo baixado é preservado em ./data/erros/ para diagnóstico

  Scenario: Verificação extra em dia de sorteio
Given que hoje é terça-feira (dia de sorteio)
When o relógio marca 22:00 BRT
Then uma verificação extra é disparada
(além da verificação periódica de 6h)
