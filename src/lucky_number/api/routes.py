"""Rotas da API."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from lucky_number.api.dependencies import get_gerador
from lucky_number.config import JOGOS
from lucky_number.models import (
    ApostaRequest,
    ApostaResponse,
    ErrorResponse,
    JogoInfo,
    JogosDisponiveisResponse,
)
from lucky_number.services.gerador import EspacoAmostralEsgotadoError, GeradorDeApostas

router = APIRouter()


@router.post(
    "/gerar-apostas",
    response_model=ApostaResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validação falhou"},
        500: {"model": ErrorResponse, "description": "Erro interno"},
    },
)
async def gerar_apostas(
    request: ApostaRequest,
    gerador: GeradorDeApostas = Depends(get_gerador),
) -> ApostaResponse:
    """Gera combinações únicas nunca sorteadas para o jogo especificado."""
    try:
        return await gerador.gerar_de_request(request)
    except EspacoAmostralEsgotadoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.get(
    "/jogos-disponiveis",
    response_model=JogosDisponiveisResponse,
)
async def jogos_disponiveis() -> JogosDisponiveisResponse:
    """Lista todos os jogos disponíveis com suas regras."""
    jogos = [
        JogoInfo(
            jogo=jogo.value,
            nome=config.nome,
            total_dezenas=config.total_dezenas,
            min_dezenas=config.min_dezenas,
            max_dezenas=config.max_dezenas,
        )
        for jogo, config in JOGOS.items()
    ]
    return JogosDisponiveisResponse(jogos=jogos)


@router.get("/health")
async def health() -> dict:
    """Health check."""
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
    }
