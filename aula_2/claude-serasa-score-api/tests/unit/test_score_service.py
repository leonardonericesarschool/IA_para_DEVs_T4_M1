"""
Testes unitários — sem I/O, sem banco, sem Redis.

Foco: domínio (CPF) e serviço (ScoreService com mocks).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from src.domain.entities import CPF, FaixaScore, ScoreResult
from src.domain.exceptions import InvalidCPFError, ScoreNotFoundError
from src.services.score_service import ScoreService


# ══════════════════════════════════════════════════════════════════════════════
# CPF Value Object
# ══════════════════════════════════════════════════════════════════════════════


class TestCPFValueObject:
    """Testa as regras do Value Object CPF."""

    # CPFs válidos para testes (gerados via algoritmo oficial)
    VALID_CPF = "52998224725"
    VALID_CPF_FORMATTED = "529.982.247-25"

    def test_aceita_cpf_valido_sem_mascara(self):
        cpf = CPF(self.VALID_CPF)
        assert cpf.value == self.VALID_CPF

    def test_aceita_cpf_valido_formatado(self):
        cpf = CPF(self.VALID_CPF_FORMATTED)
        assert cpf.value == self.VALID_CPF  # armazena só dígitos

    def test_retorna_masked_no_str(self):
        cpf = CPF(self.VALID_CPF)
        assert cpf.value not in str(cpf)  # nunca expõe CPF no str()
        assert "***" in str(cpf)

    def test_masked_property(self):
        cpf = CPF(self.VALID_CPF)
        assert cpf.masked.startswith("***")
        assert cpf.value[-2:] in cpf.masked

    def test_formatted_property(self):
        cpf = CPF(self.VALID_CPF)
        assert cpf.formatted == self.VALID_CPF_FORMATTED

    def test_rejeita_cpf_com_menos_de_11_digitos(self):
        with pytest.raises(InvalidCPFError):
            CPF("1234567890")  # 10 dígitos

    def test_rejeita_cpf_com_mais_de_11_digitos(self):
        with pytest.raises(InvalidCPFError):
            CPF("123456789012")  # 12 dígitos

    def test_rejeita_cpf_com_todos_digitos_iguais(self):
        """111.111.111-11 passa no tamanho mas falha nos dígitos verificadores."""
        with pytest.raises(InvalidCPFError):
            CPF("11111111111")

    def test_rejeita_cpf_com_digitos_verificadores_errados(self):
        with pytest.raises(InvalidCPFError):
            CPF("52998224700")  # últimos 2 dígitos incorretos

    def test_imutabilidade(self):
        cpf = CPF(self.VALID_CPF)
        with pytest.raises(Exception):  # frozen=True no dataclass
            cpf.value = "outro_cpf"  # type: ignore


# ══════════════════════════════════════════════════════════════════════════════
# FaixaScore
# ══════════════════════════════════════════════════════════════════════════════


class TestFaixaScore:
    @pytest.mark.parametrize("score,faixa_esperada", [
        (0, FaixaScore.MUITO_RUIM),
        (300, FaixaScore.MUITO_RUIM),
        (301, FaixaScore.RUIM),
        (500, FaixaScore.RUIM),
        (501, FaixaScore.REGULAR),
        (700, FaixaScore.REGULAR),
        (701, FaixaScore.BOM),
        (900, FaixaScore.BOM),
        (901, FaixaScore.MUITO_BOM),
        (1000, FaixaScore.MUITO_BOM),
    ])
    def test_from_score_retorna_faixa_correta(self, score: int, faixa_esperada: FaixaScore):
        assert FaixaScore.from_score(score) == faixa_esperada


# ══════════════════════════════════════════════════════════════════════════════
# ScoreService
# ══════════════════════════════════════════════════════════════════════════════


VALID_CPF = "52998224725"


@pytest.fixture
def mock_serasa_client():
    client = AsyncMock()
    client.consultar_score.return_value = {"score": 750}
    return client


@pytest.fixture
def mock_cache():
    cache = AsyncMock()
    cache.get.return_value = None  # cache miss por padrão
    cache.set.return_value = True
    return cache


@pytest.fixture
def score_service(mock_serasa_client, mock_cache):
    return ScoreService(serasa_client=mock_serasa_client, cache=mock_cache)


class TestScoreService:
    async def test_retorna_score_do_serasa_quando_cache_miss(
        self, score_service, mock_serasa_client, mock_cache
    ):
        result = await score_service.consultar_score(VALID_CPF, usuario_id="user_1")

        assert result.score == 750
        assert result.faixa == FaixaScore.BOM
        assert result.cache_hit is False
        mock_serasa_client.consultar_score.assert_called_once_with(VALID_CPF)

    async def test_retorna_score_do_cache_quando_cache_hit(
        self, score_service, mock_serasa_client, mock_cache
    ):
        mock_cache.get.return_value = {"score": 800}

        result = await score_service.consultar_score(VALID_CPF, usuario_id="user_1")

        assert result.score == 800
        assert result.cache_hit is True
        mock_serasa_client.consultar_score.assert_not_called()  # não chamou SERASA

    async def test_salva_no_cache_apos_consulta_serasa(
        self, score_service, mock_cache
    ):
        await score_service.consultar_score(VALID_CPF, usuario_id="user_1")
        mock_cache.set.assert_called_once_with(VALID_CPF, {"score": 750})

    async def test_levanta_invalid_cpf_para_cpf_invalido(self, score_service):
        with pytest.raises(InvalidCPFError):
            await score_service.consultar_score("00000000000", usuario_id="user_1")

    async def test_propaga_score_not_found_do_serasa(
        self, score_service, mock_serasa_client
    ):
        mock_serasa_client.consultar_score.side_effect = ScoreNotFoundError("CPF não encontrado")

        with pytest.raises(ScoreNotFoundError):
            await score_service.consultar_score(VALID_CPF, usuario_id="user_1")

    async def test_nao_falha_se_cache_set_lancar_excecao(
        self, score_service, mock_cache
    ):
        """Falha de cache não deve propagar erro para o usuário."""
        mock_cache.set.side_effect = Exception("Redis timeout")

        # Deve retornar normalmente mesmo com cache falhando
        result = await score_service.consultar_score(VALID_CPF, usuario_id="user_1")
        assert result.score == 750
