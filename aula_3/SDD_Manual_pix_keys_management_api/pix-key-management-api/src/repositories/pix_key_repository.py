"""SQLAlchemy implementation of PixKeyRepository."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models import PixKeyModel
from src.domain.models import PixKey, StatusChaveEnum


class PixKeyRepository:
    """SQLAlchemy implementation of PixKeyRepository."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session.

        Args:
            db: AsyncSession for database access
        """
        self.db = db

    async def create(self, pix_key: PixKey) -> PixKey:
        """Create a new Pix key.

        Args:
            pix_key: PixKey domain object

        Returns:
            Created PixKey with id and timestamps
        """
        db_obj = PixKeyModel(
            tipo_chave=pix_key.tipo_chave,
            valor_chave=pix_key.valor_chave,
            conta_id=pix_key.conta_id,
            cliente_id=pix_key.cliente_id,
            status=pix_key.status,
        )
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return self._to_domain(db_obj)

    async def get_by_id(self, key_id: UUID) -> PixKey | None:
        """Get Pix key by ID.

        Args:
            key_id: UUID of the Pix key

        Returns:
            PixKey if found, None otherwise
        """
        stmt = select(PixKeyModel).where(PixKeyModel.id == key_id)
        result = await self.db.execute(stmt)
        db_obj = result.scalars().first()
        return self._to_domain(db_obj) if db_obj else None

    async def get_by_cliente_tipo_valor(
        self, cliente_id: int, tipo: str, valor: str
    ) -> PixKey | None:
        """Get Pix key by client, type and value.

        Args:
            cliente_id: Client ID
            tipo: Key type
            valor: Key value

        Returns:
            PixKey if found, None otherwise
        """
        stmt = select(PixKeyModel).where(
            (PixKeyModel.cliente_id == cliente_id)
            & (PixKeyModel.tipo_chave == tipo)
            & (PixKeyModel.valor_chave == valor)
            & (PixKeyModel.status != StatusChaveEnum.DELETADA)
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalars().first()
        return self._to_domain(db_obj) if db_obj else None

    async def list_by_cliente(
        self, cliente_id: int, skip: int = 0, limit: int = 10
    ) -> tuple[list[PixKey], int]:
        """List Pix keys by client with pagination.

        Args:
            cliente_id: Client ID
            skip: Number of items to skip
            limit: Maximum items to return

        Returns:
            Tuple of (list of PixKey, total count)
        """
        # Get total count
        count_stmt = select(func.count(PixKeyModel.id)).where(
            (PixKeyModel.cliente_id == cliente_id)
            & (PixKeyModel.status != StatusChaveEnum.DELETADA)
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        stmt = (
            select(PixKeyModel)
            .where(
                (PixKeyModel.cliente_id == cliente_id)
                & (PixKeyModel.status != StatusChaveEnum.DELETADA)
            )
            .order_by(PixKeyModel.criado_em.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        return [self._to_domain(obj) for obj in db_objs], total

    async def list_by_conta(
        self, conta_id: int, skip: int = 0, limit: int = 10
    ) -> tuple[list[PixKey], int]:
        """List Pix keys by account with pagination.

        Args:
            conta_id: Account ID
            skip: Number of items to skip
            limit: Maximum items to return

        Returns:
            Tuple of (list of PixKey, total count)
        """
        # Get total count
        count_stmt = select(func.count(PixKeyModel.id)).where(
            (PixKeyModel.conta_id == conta_id)
            & (PixKeyModel.status != StatusChaveEnum.DELETADA)
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        stmt = (
            select(PixKeyModel)
            .where(
                (PixKeyModel.conta_id == conta_id)
                & (PixKeyModel.status != StatusChaveEnum.DELETADA)
            )
            .order_by(PixKeyModel.criado_em.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        return [self._to_domain(obj) for obj in db_objs], total

    async def update_status(self, key_id: UUID, new_status: str) -> PixKey | None:
        """Update Pix key status.

        Args:
            key_id: UUID of the Pix key
            new_status: New status

        Returns:
            Updated PixKey if found, None otherwise
        """
        stmt = select(PixKeyModel).where(PixKeyModel.id == key_id)
        result = await self.db.execute(stmt)
        db_obj = result.scalars().first()

        if not db_obj:
            return None

        db_obj.status = new_status
        await self.db.flush()
        await self.db.refresh(db_obj)
        return self._to_domain(db_obj)

    async def delete(self, key_id: UUID) -> bool:
        """Delete (mark as deleted) a Pix key.

        Args:
            key_id: UUID of the Pix key

        Returns:
            True if deleted, False if not found
        """
        stmt = select(PixKeyModel).where(PixKeyModel.id == key_id)
        result = await self.db.execute(stmt)
        db_obj = result.scalars().first()

        if not db_obj:
            return False

        db_obj.status = StatusChaveEnum.DELETADA
        await self.db.flush()
        return True

    @staticmethod
    def _to_domain(db_obj: PixKeyModel | None) -> PixKey | None:
        """Convert database model to domain model.

        Args:
            db_obj: Database model instance

        Returns:
            Domain model instance
        """
        if not db_obj:
            return None

        return PixKey(
            id=db_obj.id,
            tipo_chave=db_obj.tipo_chave,
            valor_chave=db_obj.valor_chave,
            conta_id=db_obj.conta_id,
            cliente_id=db_obj.cliente_id,
            status=db_obj.status,
            criado_em=db_obj.criado_em,
            atualizado_em=db_obj.atualizado_em,
        )
