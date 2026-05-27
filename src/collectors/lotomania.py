"""LotomaniaCollector — 20 bolas (0-99)."""

from src.collectors.base import BaseLotteryCollector


class LotomaniaCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Dia-De-Sorte"  # noqa: E501  # noqa: E501
    GAME_LABEL = "Lotomania"
    TABLE_NAME = "loterias_resultados_lotomania"
    JSON_PATH = "./data/lotomania.json"
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
        "Bola8",
        "Bola9",
        "Bola10",
        "Bola11",
        "Bola12",
        "Bola13",
        "Bola14",
        "Bola15",
        "Bola16",
        "Bola17",
        "Bola18",
        "Bola19",
        "Bola20",
    ]
    CONCURSO_COL = "Concurso"
