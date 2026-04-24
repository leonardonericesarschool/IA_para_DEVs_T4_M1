"""Pix Key business logic service."""
import re
from uuid import UUID
from logging import getLogger

from src.domain.models import PixKey, TipoChaveEnum, StatusChaveEnum
from src.core.exceptions import (
    ChaveDuplicadaError,
    ContaNaoElegivelError,
    ChaveNaoEncontradaError,
    FormatoChaveInvalidoError,
)
from src.repositories.pix_key_repository import PixKeyRepository

logger = getLogger(__name__)


class PixKeyService:
    """Business logic for Pix key management."""

    def __init__(self, repository: PixKeyRepository):
        """Initialize with repository.

        Args:
            repository: PixKeyRepository instance for data access
        """
        self.repository = repository

    async def criar_chave(
        self, tipo_chave: str, valor_chave: str, conta_id: int, cliente_id: int
    ) -> PixKey:
        """Create a new Pix key.

        Args:
            tipo_chave: Key type (CPF, CNPJ, EMAIL, TELEFONE)
            valor_chave: Key value
            conta_id: Account ID
            cliente_id: Client ID

        Returns:
            Created PixKey

        Raises:
            FormatoChaveInvalidoError: If key format is invalid
            ContaNaoElegivelError: If account is not eligible
            ChaveDuplicadaError: If key already exists for client
        """
        # Validate format
        self._validar_formato(tipo_chave, valor_chave)

        # Check for duplicates
        existing = await self.repository.get_by_cliente_tipo_valor(
            cliente_id, tipo_chave, valor_chave
        )
        if existing:
            logger.warning(
                f"Tentativa de criar chave duplicada",
                extra={
                    "cliente_id": cliente_id,
                    "tipo_chave": tipo_chave,
                    "valor_chave_truncado": valor_chave[:3] + "***",
                },
            )
            raise ChaveDuplicadaError()

        # Validate account eligibility
        if not await self._validar_conta_elegivel(conta_id, cliente_id):
            logger.warning(
                f"Conta não elegível para cadastro de chave",
                extra={"conta_id": conta_id, "cliente_id": cliente_id},
            )
            raise ContaNaoElegivelError()

        # Create key
        chave = PixKey(
            id=None,
            tipo_chave=tipo_chave,
            valor_chave=valor_chave,
            conta_id=conta_id,
            cliente_id=cliente_id,
            status=StatusChaveEnum.CRIADA,
        )

        created_chave = await self.repository.create(chave)

        logger.info(
            f"Chave Pix criada com sucesso",
            extra={
                "chave_id": str(created_chave.id),
                "cliente_id": cliente_id,
                "tipo_chave": tipo_chave,
            },
        )

        return created_chave

    async def get_chave(self, chave_id: UUID) -> PixKey | None:
        """Get Pix key by ID.

        Args:
            chave_id: Pix key ID

        Returns:
            PixKey if found, None otherwise
        """
        chave = await self.repository.get_by_id(chave_id)

        if chave and chave.status == StatusChaveEnum.DELETADA:
            return None

        return chave

    async def listar_por_cliente(
        self, cliente_id: int, skip: int = 0, limit: int = 10
    ) -> tuple[list[PixKey], int]:
        """List Pix keys for a client.

        Args:
            cliente_id: Client ID
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            Tuple of (list of PixKey, total count)
        """
        chaves, total = await self.repository.list_by_cliente(cliente_id, skip, limit)

        logger.info(
            f"Chaves Pix listadas por cliente",
            extra={"cliente_id": cliente_id, "total": total, "limit": limit},
        )

        return chaves, total

    async def listar_por_conta(
        self, conta_id: int, skip: int = 0, limit: int = 10
    ) -> tuple[list[PixKey], int]:
        """List Pix keys for an account.

        Args:
            conta_id: Account ID
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            Tuple of (list of PixKey, total count)
        """
        chaves, total = await self.repository.list_by_conta(conta_id, skip, limit)

        logger.info(
            f"Chaves Pix listadas por conta",
            extra={"conta_id": conta_id, "total": total, "limit": limit},
        )

        return chaves, total

    async def deletar_chave(self, chave_id: UUID) -> bool:
        """Delete a Pix key (mark as deleted).

        Args:
            chave_id: Pix key ID

        Returns:
            True if deleted, False if not found
        """
        chave = await self.repository.get_by_id(chave_id)

        if not chave:
            logger.warning(
                f"Tentativa de deletar chave não encontrada",
                extra={"chave_id": str(chave_id)},
            )
            return False

        deleted = await self.repository.delete(chave_id)

        if deleted:
            logger.info(
                f"Chave Pix deletada com sucesso",
                extra={
                    "chave_id": str(chave_id),
                    "cliente_id": chave.cliente_id,
                },
            )

        return deleted

    def _validar_formato(self, tipo_chave: str, valor_chave: str) -> None:
        """Validate Pix key format based on type.

        Args:
            tipo_chave: Key type
            valor_chave: Key value

        Raises:
            FormatoChaveInvalidoError: If format is invalid
        """
        validators = {
            TipoChaveEnum.CPF.value: self._validar_cpf,
            TipoChaveEnum.CNPJ.value: self._validar_cnpj,
            TipoChaveEnum.EMAIL.value: self._validar_email,
            TipoChaveEnum.TELEFONE.value: self._validar_telefone,
        }

        validator = validators.get(tipo_chave)
        if not validator:
            raise FormatoChaveInvalidoError(f"Tipo de chave inválido: {tipo_chave}")

        validator(valor_chave)

    @staticmethod
    def _validar_cpf(cpf: str) -> None:
        """Validate CPF format and algorithm.

        Args:
            cpf: CPF string (11 digits)

        Raises:
            FormatoChaveInvalidoError: If CPF is invalid
        """
        # Remove non-digits
        cpf_clean = re.sub(r"\D", "", cpf)

        if len(cpf_clean) != 11:
            raise FormatoChaveInvalidoError("CPF deve conter 11 dígitos")

        # Check if all digits are the same (invalid CPF)
        if cpf_clean == cpf_clean[0] * 11:
            raise FormatoChaveInvalidoError("CPF com todos os dígitos iguais é inválido")

        # Validate CPF algorithm (Modulo 11)
        if not PixKeyService._validar_cpf_algoritmo(cpf_clean):
            raise FormatoChaveInvalidoError("CPF com dígito verificador inválido")

    @staticmethod
    def _validar_cpf_algoritmo(cpf: str) -> bool:
        """Validate CPF using modulo 11 algorithm.

        Args:
            cpf: 11-digit CPF string

        Returns:
            True if valid, False otherwise
        """
        # First digit
        sum_val = sum(int(cpf[i]) * (10 - i) for i in range(9))
        first_digit = 11 - (sum_val % 11)
        first_digit = 0 if first_digit >= 10 else first_digit

        if int(cpf[9]) != first_digit:
            return False

        # Second digit
        sum_val = sum(int(cpf[i]) * (11 - i) for i in range(10))
        second_digit = 11 - (sum_val % 11)
        second_digit = 0 if second_digit >= 10 else second_digit

        if int(cpf[10]) != second_digit:
            return False

        return True

    @staticmethod
    def _validar_cnpj(cnpj: str) -> None:
        """Validate CNPJ format and algorithm.

        Args:
            cnpj: CNPJ string (14 digits)

        Raises:
            FormatoChaveInvalidoError: If CNPJ is invalid
        """
        # Remove non-digits
        cnpj_clean = re.sub(r"\D", "", cnpj)

        if len(cnpj_clean) != 14:
            raise FormatoChaveInvalidoError("CNPJ deve conter 14 dígitos")

        # Check if all digits are the same (invalid CNPJ)
        if cnpj_clean == cnpj_clean[0] * 14:
            raise FormatoChaveInvalidoError("CNPJ com todos os dígitos iguais é inválido")

        # Validate CNPJ algorithm (Modulo 11)
        if not PixKeyService._validar_cnpj_algoritmo(cnpj_clean):
            raise FormatoChaveInvalidoError("CNPJ com dígito verificador inválido")

    @staticmethod
    def _validar_cnpj_algoritmo(cnpj: str) -> bool:
        """Validate CNPJ using modulo 11 algorithm.

        Args:
            cnpj: 14-digit CNPJ string

        Returns:
            True if valid, False otherwise
        """
        # First digit
        sum_val = sum(int(cnpj[i]) * (6 - (i % 8)) for i in range(8))
        sum_val += sum(int(cnpj[i + 8]) * (10 - (i % 8)) for i in range(4))
        first_digit = 11 - (sum_val % 11)
        first_digit = 0 if first_digit >= 10 else first_digit

        if int(cnpj[8]) != first_digit:
            return False

        # Second digit
        sum_val = sum(int(cnpj[i]) * (7 - (i % 8)) for i in range(9))
        sum_val += sum(int(cnpj[i + 9]) * (10 - (i % 8)) for i in range(3))
        second_digit = 11 - (sum_val % 11)
        second_digit = 0 if second_digit >= 10 else second_digit

        if int(cnpj[9]) != second_digit:
            return False

        return True

    @staticmethod
    def _validar_email(email: str) -> None:
        """Validate email format.

        Args:
            email: Email address

        Raises:
            FormatoChaveInvalidoError: If email format is invalid
        """
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            raise FormatoChaveInvalidoError("Formato de email inválido")

        if len(email) > 254:
            raise FormatoChaveInvalidoError("Email muito longo (máximo 254 caracteres)")

    @staticmethod
    def _validar_telefone(telefone: str) -> None:
        """Validate phone number format.

        Args:
            telefone: Phone number

        Raises:
            FormatoChaveInvalidoError: If phone format is invalid
        """
        # Remove non-digits
        phone_clean = re.sub(r"\D", "", telefone)

        if len(phone_clean) < 10 or len(phone_clean) > 11:
            raise FormatoChaveInvalidoError("Telefone deve conter 10 ou 11 dígitos")

        # Check if all digits are the same
        if phone_clean == phone_clean[0] * len(phone_clean):
            raise FormatoChaveInvalidoError("Telefone com todos os dígitos iguais é inválido")

    async def _validar_conta_elegivel(self, conta_id: int, cliente_id: int) -> bool:
        """Validate if account is eligible for Pix key (mock for MVP).

        Args:
            conta_id: Account ID
            cliente_id: Client ID

        Returns:
            True if eligible, False otherwise

        Note:
            This is a mock implementation. In production, this would call
            an external account service to validate eligibility.
        """
        # TODO: Integrate with account service
        # For MVP, we accept all accounts (return True)
        return True
