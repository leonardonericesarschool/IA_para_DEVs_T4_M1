"""SQLAlchemy implementation of PixKey repository"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, select
from src.repositories import PixKeyRepository, PixKeyAuditRepository
from src.models.database_models import PixKeyModel, PixKeyAuditModel, UserModel
from src.entities import PixKeyType, PixKeyStatus, PixKeyValidationStatus, PixKeyAuditOperation
from src.entities.pix_key import PixKey
from src.entities.pix_key_audit import PixKeyAudit
from src.exceptions import DatabaseError


class SQLAlchemyPixKeyRepository(PixKeyRepository):
    """SQLAlchemy implementation of PixKey repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(
        self,
        user_id: UUID,
        key_type: PixKeyType,
        key_value_hash: str,
        key_value_masked: str,
        alias: Optional[str] = None,
        validation_status: str = "VALID"
    ) -> dict:
        """Create and persist a new PixKey"""
        try:
            db_pix_key = PixKeyModel(
                user_id=user_id,
                key_type=key_type,
                key_value_hash=key_value_hash,
                key_value_masked=key_value_masked,
                alias=alias,
                validation_status=PixKeyValidationStatus(validation_status),
                status=PixKeyStatus.ACTIVE
            )
            self.db.add(db_pix_key)
            self.db.commit()
            self.db.refresh(db_pix_key)
            return self._db_model_to_dict(db_pix_key)
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create PixKey: {str(e)}")
    
    async def get_by_id(self, key_id: UUID) -> Optional[dict]:
        """Get PixKey by primary key"""
        try:
            db_key = self.db.query(PixKeyModel).filter(PixKeyModel.key_id == key_id).first()
            return self._db_model_to_dict(db_key) if db_key else None
        except Exception as e:
            raise DatabaseError(f"Failed to get PixKey: {str(e)}")
    
    async def get_by_hash(self, user_id: UUID, key_hash: str) -> Optional[dict]:
        """Get PixKey by user and key hash (for duplicate detection)"""
        try:
            db_key = self.db.query(PixKeyModel).filter(
                and_(
                    PixKeyModel.user_id == user_id,
                    PixKeyModel.key_value_hash == key_hash
                )
            ).first()
            return self._db_model_to_dict(db_key) if db_key else None
        except Exception as e:
            raise DatabaseError(f"Failed to get PixKey by hash: {str(e)}")
    
    async def get_all_for_user(self, user_id: UUID) -> List[dict]:
        """Get all PixKeys for a user"""
        try:
            db_keys = self.db.query(PixKeyModel).filter(PixKeyModel.user_id == user_id).all()
            return [self._db_model_to_dict(key) for key in db_keys]
        except Exception as e:
            raise DatabaseError(f"Failed to get user PixKeys: {str(e)}")
    
    async def get_for_user_filtered(
        self,
        user_id: UUID,
        status: Optional[PixKeyStatus] = None,
        key_type: Optional[PixKeyType] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[dict], int]:
        """Get filtered PixKeys for user with pagination"""
        try:
            query = self.db.query(PixKeyModel).filter(PixKeyModel.user_id == user_id)
            
            if status:
                query = query.filter(PixKeyModel.status == status)
            if key_type:
                query = query.filter(PixKeyModel.key_type == key_type)
            
            total = query.count()
            db_keys = query.order_by(PixKeyModel.created_at.desc()).offset(offset).limit(limit).all()
            
            return [self._db_model_to_dict(key) for key in db_keys], total
        except Exception as e:
            raise DatabaseError(f"Failed to get filtered PixKeys: {str(e)}")
    
    async def count_for_user(self, user_id: UUID) -> int:
        """Count active PixKeys for user"""
        try:
            count = self.db.query(PixKeyModel).filter(
                and_(
                    PixKeyModel.user_id == user_id,
                    PixKeyModel.status == PixKeyStatus.ACTIVE
                )
            ).count()
            return count
        except Exception as e:
            raise DatabaseError(f"Failed to count user PixKeys: {str(e)}")
    
    async def update_status(self, key_id: UUID, status: PixKeyStatus) -> Optional[dict]:
        """Update PixKey status"""
        try:
            db_key = self.db.query(PixKeyModel).filter(PixKeyModel.key_id == key_id).first()
            if db_key:
                db_key.status = status
                if status == PixKeyStatus.INACTIVE:
                    db_key.is_preferred = False
                self.db.commit()
                self.db.refresh(db_key)
            return self._db_model_to_dict(db_key) if db_key else None
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update PixKey status: {str(e)}")
    
    async def update_alias(self, key_id: UUID, alias: Optional[str]) -> Optional[dict]:
        """Update PixKey alias"""
        try:
            db_key = self.db.query(PixKeyModel).filter(PixKeyModel.key_id == key_id).first()
            if db_key:
                db_key.alias = alias
                self.db.commit()
                self.db.refresh(db_key)
            return self._db_model_to_dict(db_key) if db_key else None
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update PixKey alias: {str(e)}")
    
    async def delete(self, key_id: UUID) -> bool:
        """Delete PixKey permanently"""
        try:
            db_key = self.db.query(PixKeyModel).filter(PixKeyModel.key_id == key_id).first()
            if db_key:
                self.db.delete(db_key)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to delete PixKey: {str(e)}")
    
    async def verify_ownership(self, user_id: UUID, key_id: UUID) -> bool:
        """Verify that user owns the key"""
        try:
            result = self.db.query(PixKeyModel).filter(
                and_(
                    PixKeyModel.key_id == key_id,
                    PixKeyModel.user_id == user_id
                )
            ).first()
            return result is not None
        except Exception as e:
            raise DatabaseError(f"Failed to verify ownership: {str(e)}")
    
    @staticmethod
    def _db_model_to_dict(db_model: Optional[PixKeyModel]) -> Optional[dict]:
        """Convert SQLAlchemy model to dictionary"""
        if not db_model:
            return None
        return {
            "key_id": str(db_model.key_id),
            "user_id": str(db_model.user_id),
            "key_type": db_model.key_type.value,
            "key_value_hash": db_model.key_value_hash,
            "key_value_masked": db_model.key_value_masked,
            "status": db_model.status.value,
            "alias": db_model.alias,
            "is_preferred": db_model.is_preferred,
            "validation_status": db_model.validation_status.value,
            "validation_error": db_model.validation_error,
            "pix_network_id": db_model.pix_network_id,
            "created_at": db_model.created_at,
            "updated_at": db_model.updated_at,
            "revalidated_at": db_model.revalidated_at
        }


class SQLAlchemyPixKeyAuditRepository(PixKeyAuditRepository):
    """SQLAlchemy implementation of PixKey audit repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_audit_log(
        self,
        key_id: UUID,
        user_id: UUID,
        operation: PixKeyAuditOperation,
        status: str,
        details: Optional[dict] = None
    ) -> dict:
        """Create audit log entry"""
        try:
            db_audit = PixKeyAuditModel(
                key_id=key_id,
                user_id=user_id,
                operation=operation,
                status=status,
                details=details or {}
            )
            self.db.add(db_audit)
            self.db.commit()
            self.db.refresh(db_audit)
            return self._db_model_to_dict(db_audit)
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create audit log: {str(e)}")
    
    async def get_audit_trail_for_key(self, key_id: UUID, limit: int = 50) -> List[dict]:
        """Get audit trail for specific key"""
        try:
            db_audits = self.db.query(PixKeyAuditModel).filter(
                PixKeyAuditModel.key_id == key_id
            ).order_by(PixKeyAuditModel.timestamp.desc()).limit(limit).all()
            return [self._db_model_to_dict(audit) for audit in db_audits]
        except Exception as e:
            raise DatabaseError(f"Failed to get key audit trail: {str(e)}")
    
    async def get_audit_trail_for_user(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[dict], int]:
        """Get audit trail for user with pagination"""
        try:
            query = self.db.query(PixKeyAuditModel).filter(PixKeyAuditModel.user_id == user_id)
            total = query.count()
            db_audits = query.order_by(PixKeyAuditModel.timestamp.desc()).offset(offset).limit(limit).all()
            return [self._db_model_to_dict(audit) for audit in db_audits], total
        except Exception as e:
            raise DatabaseError(f"Failed to get user audit trail: {str(e)}")
    
    @staticmethod
    def _db_model_to_dict(db_model: Optional[PixKeyAuditModel]) -> Optional[dict]:
        """Convert SQLAlchemy model to dictionary"""
        if not db_model:
            return None
        return {
            "audit_id": str(db_model.audit_id),
            "key_id": str(db_model.key_id),
            "user_id": str(db_model.user_id),
            "operation": db_model.operation.value,
            "status": db_model.status,
            "details": db_model.details,
            "timestamp": db_model.timestamp
        }
