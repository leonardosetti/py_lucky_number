"""SuperseteCollector — 7 colunas (0-9)."""

from src.collectors.base import BaseLotteryCollector


class SuperseteCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Dia-De-Sorte"  # noqa: E501  # noqa: E501
    GAME_LABEL = "Supersete"
    TABLE_NAME = "loterias_resultados_supersete"
    JSON_PATH = "./data/supersete.json"
    COLUMNS = [
        "Concurso",
        "Data Sorteio",
        "Coluna 1",
        "Coluna 2",
        "Coluna 3",
        "Coluna 4",
        "Coluna 5",
        "Coluna 6",
        "Coluna 7",
    ]
    CONCURSO_COL = "Concurso"
    ball_prefix = "Coluna"
    has_dezenas = False
