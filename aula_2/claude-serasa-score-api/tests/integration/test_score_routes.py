"""
Testes de integração — testam a API HTTP completa com mocks de infra.

Usa TestClient do FastAPI (HTTPX) + override de dependências.
Não requer banco real nem Redis — apenas as dependências externas são mockadas.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.main import app
from src.core.dependencies import get_score_service, get_current_user
from src.domain.entities import CPF, FaixaScore, ScoreResult
from src.domain.exceptions import (
    InvalidCPFError,
    ScoreNotFoundError,
    ScoreServiceUnavailableError,
)
from datetime import datetime, timezone

VALID_CPF = "52998224725"
VALID_CPF_FORMATTED = "529.982.247-25"

# Score result fixture reutilizável
def make_score_result(score: int = 750, cache_hit: bool = False) -> ScoreResult:
    cpf = CPF(VALID_CPF)
    return ScoreResult(
        cpf=cpf,
        score=score,
        faixa=FaixaScore.from_score(score),
        consultado_em=datetime.now(tz=timezone.utc),
        cache_hit=cache_hit,
    )


@pytest.fixture
def mock_score_service():
    service = AsyncMock()
    service.consultar_score.return_value = make_score_result()
    return service


@pytest.fixture
def client(mock_score_service):
    """TestClient com dependências sobrescritas."""
    app.dependency_overrides[get_score_service] = lambda: mock_score_service
    app.dependency_overrides[get_current_user] = lambda: "test_user"
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestScoreEndpoint:
    def test_consulta_score_retorna_200(self, client, mock_score_service):
        response = client.post("/v1/score/consultar", json={"cpf": VALID_CPF_FORMATTED})

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 750
        assert data["faixa"]["codigo"] == "bom"
        assert "***" in data["cpf_masked"]  # CPF nunca exposto completo
        assert "cache_hit" in data

    def test_resposta_inclui_request_id_header(self, client):
        response = client.post("/v1/score/consultar", json={"cpf": VALID_CPF})
        assert "x-request-id" in response.headers

    def test_cpf_invalido_retorna_422(self, client, mock_score_service):
        mock_score_service.consultar_score.side_effect = InvalidCPFError("CPF inválido")

        response = client.post("/v1/score/consultar", json={"cpf": "00000000000"})

        assert response.status_code == 422
        assert response.json()["error"] == "invalid_cpf"

    def test_cpf_nao_encontrado_retorna_404(self, client, mock_score_service):
        mock_score_service.consultar_score.side_effect = ScoreNotFoundError("Não encontrado")

        response = client.post("/v1/score/consultar", json={"cpf": VALID_CPF})

        assert response.status_code == 404
        assert response.json()["error"] == "score_not_found"

    def test_serasa_indisponivel_retorna_503(self, client, mock_score_service):
        mock_score_service.consultar_score.side_effect = ScoreServiceUnavailableError("Timeout")

        response = client.post("/v1/score/consultar", json={"cpf": VALID_CPF})

        assert response.status_code == 503
        assert response.json()["error"] == "service_unavailable"

    def test_sem_api_key_retorna_401(self):
        """Sem override de autenticação — deve rejeitar."""
        with TestClient(app) as c:
            response = c.post("/v1/score/consultar", json={"cpf": VALID_CPF})
        assert response.status_code == 401

    def test_cache_hit_flag_na_resposta(self, client, mock_score_service):
        mock_score_service.consultar_score.return_value = make_score_result(cache_hit=True)

        response = client.post("/v1/score/consultar", json={"cpf": VALID_CPF})

        assert response.status_code == 200
        assert response.json()["cache_hit"] is True

    def test_cpf_com_mascara_aceito(self, client):
        response = client.post("/v1/score/consultar", json={"cpf": "529.982.247-25"})
        assert response.status_code == 200

    def test_health_check_retorna_ok(self, client):
        response = client.get("/v1/score/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
