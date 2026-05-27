"""DiadesorteCollector — 7 bolas + mês."""

from src.collectors.base import BaseLotteryCollector


class DiadesorteCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Dia-De-Sorte"  # noqa: E501  # noqa: E501
    GAME_LABEL = "Diadesorte"
    TABLE_NAME = "loterias_resultados_diadesorte"
    JSON_PATH = "./data/diadesorte.json"
    COLUMNS = [
        "Concurso",
        "Data Sorteio",
        "Bola1",
        "Bola2",
        "Bola3",
        "Bola4",
        "Bola5",
        "Bola6",
        "Bola7",
        "Mês da Sorte",
    ]
    CONCURSO_COL = "Concurso"
