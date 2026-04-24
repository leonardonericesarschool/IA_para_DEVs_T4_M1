"""Repository abstraction layer using Protocol (DIP principle)."""
from typing import Protocol, AsyncIterator
from uuid import UUID

from src.domain.models import PixKey


class IPixKeyRepository(Protocol):
    """Repository interface for Pix key operations."""

    async def create(self, pix_key: PixKey) -> PixKey:
        """Create a new Pix key.

        Args:
            pix_key: PixKey domain object

        Returns:
            Created PixKey with id and timestamps

        Raises:
            ChaveDuplicadaError: If key already exists for cliente
        """
        ...

    async def get_by_id(self, key_id: UUID) -> PixKey | None:
        """Get Pix key by ID.

        Args:
            key_id: UUID of the Pix key

        Returns:
            PixKey if found, None otherwise
        """
        ...

    async def get_by_cliente_tipo_valor(
        self, cliente_id: int, tipo: str, valor: str
    ) -> PixKey | None:
        """Get Pix key by client, type and value.

        Args:
            cliente_id: Client ID
            tipo: Key type (CPF, CNPJ, EMAIL, TELEFONE)
            valor: Key value

        Returns:
            PixKey if found, None otherwise
        """
        ...

    async def list_by_cliente(
        self, cliente_id: int, skip: int = 0, limit: int = 10
    ) -> tuple[list[PixKey], int]:
        """List Pix keys by client with pagination.

        Args:
            cliente_id: Client ID
            skip: Number of items to skip (pagination)
            limit: Maximum items to return

        Returns:
            Tuple of (list of PixKey, total count)
        """
        ...

    async def list_by_conta(
        self, conta_id: int, skip: int = 0, limit: int = 10
    ) -> tuple[list[PixKey], int]:
        """List Pix keys by account with pagination.

        Args:
            conta_id: Account ID
            skip: Number of items to skip (pagination)
            limit: Maximum items to return

        Returns:
            Tuple of (list of PixKey, total count)
        """
        ...

    async def update_status(self, key_id: UUID, new_status: str) -> PixKey | None:
        """Update Pix key status.

        Args:
            key_id: UUID of the Pix key
            new_status: New status (CRIADA, CONFIRMADA, DELETADA)

        Returns:
            Updated PixKey if found, None otherwise
        """
        ...

    async def delete(self, key_id: UUID) -> bool:
        """Delete (mark as deleted) a Pix key.

        Args:
            key_id: UUID of the Pix key

        Returns:
            True if deleted, False if not found
        """
        ...
