"""DuplasenaCollector — 6+6 bolas (2 sorteios)."""
from src.collectors.base import BaseLotteryCollector


class DuplasenaCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Dupla-Sena"
    GAME_LABEL = "Duplasena"
    TABLE_NAME = "loterias_resultados_duplasena"
    JSON_PATH = "./data/duplasena.json"
    COLUMNS = ['Concurso', 'Data Sorteio', 'Bola1 sorteio 1', 'Bola2 sorteio 1', 'Bola3 sorteio 1', 'Bola4 Sorteio 1', 'Bola5 sorteio 1', 'Bola6 sorteio 1', 'Bola1 sorteio 2', 'Bola2 sorteio 2', 'Bola3 sorteio 2', 'Bola4 Sorteio 2', 'Bola5 sorteio 2', 'Bola6 sorteio 2']
    CONCURSO_COL = "Concurso"
