from sqlalchemy import Column, Integer, DateTime, String, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
from typing import Any, Dict
import json

from app.core.database import Base

class TimestampMixin:
    """Mixin to add timestamp fields to models"""
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

class BaseModel(Base, TimestampMixin):
    """Base model class with common fields and methods"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    @declared_attr
    def __tablename__(cls):
        # Convert CamelCase to snake_case for table names
        import re
        return re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__).lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def to_json(self) -> str:
        """Convert model instance to JSON string"""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model instance from dictionary"""
        return cls(**data)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

class SoftDeleteMixin:
    """Mixin to add soft delete functionality"""
    
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self):
        """Mark record as deleted"""
        self.is_deleted = True
        self.deleted_at = func.now()
    
    def restore(self):
        """Restore soft deleted record"""
        self.is_deleted = False
        self.deleted_at = None 