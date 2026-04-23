"""
Cliente HTTP para a API externa do SERASA.

Responsabilidades:
- Fazer a chamada HTTP com timeout e retry
- Mapear erros HTTP para exceções de domínio
- NUNCA logar o CPF completo nem a API key

Não contém lógica de negócio — apenas I/O + mapeamento de erros.
"""

import logging
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.core.config import Settings
from src.domain.exceptions import (
    ScoreNotFoundError,
    ScoreRateLimitError,
    ScoreServiceUnavailableError,
)

logger = logging.getLogger(__name__)


class SerasaHTTPClient:
    """
    Wrapper sobre httpx.AsyncClient para a API SERASA.

    - Retry automático com backoff exponencial para erros 5xx e timeouts
    - Sem retry em 4xx (erros de cliente, sem sentido repetir)
    - API key injetada via header — nunca em query params (aparece em logs de servidor)
    """

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.serasa_api_url
        self._timeout = settings.serasa_timeout_seconds
        self._max_retries = settings.serasa_max_retries
        self._headers = {
            "X-Api-Key": settings.serasa_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def consultar_score(self, cpf_digits: str) -> dict[str, Any]:
        """
        Consulta o score de crédito para um CPF.

        Args:
            cpf_digits: apenas os 11 dígitos, sem máscara.

        Returns:
            Dicionário com os dados brutos do SERASA.

        Raises:
            ScoreNotFoundError: CPF sem cadastro no SERASA.
            ScoreRateLimitError: Limite de consultas atingido.
            ScoreServiceUnavailableError: SERASA fora do ar ou timeout.
        """
        return await self._fetch_with_retry(cpf_digits)

    @retry(
        retry=retry_if_exception_type(ScoreServiceUnavailableError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def _fetch_with_retry(self, cpf_digits: str) -> dict[str, Any]:
        # CPF mascarado no log — nunca o valor completo
        cpf_log = f"***{cpf_digits[6:9]}-{cpf_digits[9:]}"
        logger.info("Consultando SERASA para CPF %s", cpf_log)

        async with httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=httpx.Timeout(self._timeout),
        ) as client:
            try:
                response = await client.get(f"/score/{cpf_digits}")
            except httpx.TimeoutException as exc:
                logger.warning("Timeout na consulta SERASA para CPF %s", cpf_log)
                raise ScoreServiceUnavailableError(
                    "SERASA não respondeu dentro do tempo limite"
                ) from exc
            except httpx.NetworkError as exc:
                logger.error("Erro de rede ao consultar SERASA: %s", exc)
                raise ScoreServiceUnavailableError(
                    "Erro de conexão com o serviço SERASA"
                ) from exc

        return self._handle_response(response, cpf_log)

    def _handle_response(self, response: httpx.Response, cpf_log: str) -> dict[str, Any]:
        """Mapeia status HTTP para exceções de domínio."""
        if response.status_code == 200:
            return response.json()

        if response.status_code == 404:
            raise ScoreNotFoundError(
                f"Nenhum registro encontrado para CPF {cpf_log}",
                details={"cpf_masked": cpf_log},
            )

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            raise ScoreRateLimitError(
                "Limite de consultas SERASA atingido",
                details={"retry_after_seconds": int(retry_after)},
            )

        if response.status_code >= 500:
            logger.error(
                "SERASA retornou %d para CPF %s: %s",
                response.status_code, cpf_log, response.text[:200],
            )
            raise ScoreServiceUnavailableError(
                f"SERASA retornou erro {response.status_code}",
                details={"status_code": response.status_code},
            )

        # 4xx inesperado
        logger.warning(
            "SERASA retornou %d inesperado para CPF %s",
            response.status_code, cpf_log,
        )
        raise ScoreServiceUnavailableError(
            f"Resposta inesperada do SERASA: {response.status_code}"
        )
