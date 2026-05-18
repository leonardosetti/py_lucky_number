"""FederalCollector — 5 prêmios."""
from src.collectors.base import BaseLotteryCollector


class FederalCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Federal"
    GAME_LABEL = "Federal"
    TABLE_NAME = "loterias_resultados_federal"
    JSON_PATH = "./data/federal.json"
    COLUMNS = ['Extração', 'Data Sorteio', '1º prêmio', 'Valor 1º prêmio', '2º prêmio', 'Valor 2º prêmio', '3º prêmio', 'Valor 3º prêmio', '4º prêmio', 'Valor 4º prêmio', '5º prêmio', 'Valor 5º prêmio']
    CONCURSO_COL = "Extração"
