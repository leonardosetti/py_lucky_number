"""MaismilionariaCollector — 6 números + 2 trevos."""
from src.collectors.base import BaseLotteryCollector


class MaismilionariaCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Mais-Milionaria"
    GAME_LABEL = "Maismilionaria"
    TABLE_NAME = "loterias_resultados_maismilionaria"
    JSON_PATH = "./data/maismilionaria.json"
    COLUMNS = ['Concurso', 'Data Sorteio', 'Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6', 'Trevo1', 'Trevo2']
    CONCURSO_COL = "Concurso"
