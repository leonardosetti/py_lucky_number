"""Contratos Pydantic para a API de Lucky Number."""

from datetime import datetime, UTC

from pydantic import BaseModel, Field, model_validator

from lucky_number.config import JOGOS, Jogo, MINIMO_INEGOCIAVEL


class ApostaRequest(BaseModel):
    jogo: Jogo
    quantidade_apostas: int = Field(ge=1, le=100)
    dezenas_por_aposta: int = Field(ge=1)

    @model_validator(mode="after")
    def validar_dezenas(self) -> "ApostaRequest":
        config = JOGOS[self.jogo]

        if self.dezenas_por_aposta < MINIMO_INEGOCIAVEL:
            raise ValueError(
                f"Mínimo de {MINIMO_INEGOCIAVEL} dezenas é inegociável"
            )

        if self.dezenas_por_aposta > config.max_dezenas:
            raise ValueError(
                f"Máximo de {config.max_dezenas} dezenas para {config.nome}"
            )

        if self.dezenas_por_aposta > config.total_dezenas:
            raise ValueError(
                f"Não é possível apostar mais dezenas que o total disponível ({config.total_dezenas})"
            )

        return self


class ApostaResponse(BaseModel):
    jogo: str
    nome_jogo: str
    dezenas_por_aposta: int
    apostas: list[list[int]]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class JogoInfo(BaseModel):
    jogo: str
    nome: str
    total_dezenas: int
    min_dezenas: int
    max_dezenas: int


class JogosDisponiveisResponse(BaseModel):
    jogos: list[JogoInfo]


class ErrorResponse(BaseModel):
    detail: str
    status_code: int
