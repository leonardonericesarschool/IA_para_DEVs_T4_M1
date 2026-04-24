"""Unit tests for PixKeyService validation logic."""
import pytest

from src.services.pix_key_service import PixKeyService
from src.core.exceptions import FormatoChaveInvalidoError


class TestPixKeyServiceValidation:
    """Test suite for PixKeyService validation methods."""

    def test_validar_cpf_valido(self):
        """Test valid CPF validation."""
        # Use a valid CPF: 11144477735 (generated from algorithm)
        service = PixKeyService(None)
        service._validar_formato("CPF", "11144477735")  # Should not raise

    def test_validar_cpf_invalido_formato(self):
        """Test CPF with invalid number of digits."""
        service = PixKeyService(None)
        with pytest.raises(FormatoChaveInvalidoError, match="11 dígitos"):
            service._validar_formato("CPF", "123456789")  # Only 9 digits

    def test_validar_cpf_todos_digitos_iguais(self):
        """Test CPF with all same digits (invalid)."""
        service = PixKeyService(None)
        with pytest.raises(FormatoChaveInvalidoError, match="iguais"):
            service._validar_formato("CPF", "11111111111")

    def test_validar_cnpj_valido(self):
        """Test valid CNPJ validation."""
        # Use a valid CNPJ: 11222333000181 (generated from algorithm)
        service = PixKeyService(None)
        service._validar_formato("CNPJ", "11222333000181")  # Should not raise

    def test_validar_cnpj_invalido_formato(self):
        """Test CNPJ with invalid number of digits."""
        service = PixKeyService(None)
        with pytest.raises(FormatoChaveInvalidoError, match="14 dígitos"):
            service._validar_formato("CNPJ", "1234567890")  # Only 10 digits

    def test_validar_cnpj_todos_digitos_iguais(self):
        """Test CNPJ with all same digits (invalid)."""
        service = PixKeyService(None)
        with pytest.raises(FormatoChaveInvalidoError, match="iguais"):
            service._validar_formato("CNPJ", "11111111111111")

    def test_validar_email_valido(self):
        """Test valid email validation."""
        service = PixKeyService(None)
        service._validar_formato("EMAIL", "test@example.com")  # Should not raise

    def test_validar_email_invalido_sem_arroba(self):
        """Test email without @ symbol."""
        service = PixKeyService(None)
        with pytest.raises(FormatoChaveInvalidoError, match="email inválido"):
            service._validar_formato("EMAIL", "testexample.com")

    def test_validar_email_invalido_sem_dominio(self):
        """Test email without domain."""
        service = PixKeyService(None)
        with pytest.raises(FormatoChaveInvalidoError, match="email inválido"):
            service._validar_formato("EMAIL", "test@")

    def test_validar_email_muito_longo(self):
        """Test email that exceeds maximum length."""
        service = PixKeyService(None)
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(FormatoChaveInvalidoError, match="muito longo"):
            service._validar_formato("EMAIL", long_email)

    def test_validar_telefone_valido_10_digitos(self):
        """Test valid phone with 10 digits."""
        service = PixKeyService(None)
        service._validar_formato("TELEFONE", "1133334444")  # Should not raise

    def test_validar_telefone_valido_11_digitos(self):
        """Test valid phone with 11 digits."""
        service = PixKeyService(None)
        service._validar_formato("TELEFONE", "11987654321")  # Should not raise

    def test_validar_telefone_invalido_poucos_digitos(self):
        """Test phone with too few digits."""
        service = PixKeyService(None)
        with pytest.raises(FormatoChaveInvalidoError, match="10 ou 11 dígitos"):
            service._validar_formato("TELEFONE", "123456789")  # Only 9 digits

    def test_validar_telefone_invalido_muitos_digitos(self):
        """Test phone with too many digits."""
        service = PixKeyService(None)
        with pytest.raises(FormatoChaveInvalidoError, match="10 ou 11 dígitos"):
            service._validar_formato("TELEFONE", "123456789012")  # 12 digits

    def test_validar_telefone_todos_digitos_iguais(self):
        """Test phone with all same digits (invalid)."""
        service = PixKeyService(None)
        with pytest.raises(FormatoChaveInvalidoError, match="iguais"):
            service._validar_formato("TELEFONE", "1111111111")

    def test_validar_tipo_chave_invalido(self):
        """Test invalid key type."""
        service = PixKeyService(None)
        with pytest.raises(FormatoChaveInvalidoError, match="Tipo de chave inválido"):
            service._validar_formato("INVALIDO", "value")


class TestCPFAlgorithm:
    """Test CPF validation algorithm."""

    def test_cpf_algoritmo_valido_1(self):
        """Test CPF algorithm with valid CPF 1."""
        assert PixKeyService._validar_cpf_algoritmo("11144477735") is True

    def test_cpf_algoritmo_valido_2(self):
        """Test CPF algorithm with valid CPF 2."""
        assert PixKeyService._validar_cpf_algoritmo("12345678901") is False  # Invalid check digits


class TestCNPJAlgorithm:
    """Test CNPJ validation algorithm."""

    def test_cnpj_algoritmo_valido(self):
        """Test CNPJ algorithm with valid CNPJ."""
        assert PixKeyService._validar_cnpj_algoritmo("11222333000181") is True

    def test_cnpj_algoritmo_invalido(self):
        """Test CNPJ algorithm with invalid CNPJ."""
        assert PixKeyService._validar_cnpj_algoritmo("12345678901234") is False  # Invalid check digits
