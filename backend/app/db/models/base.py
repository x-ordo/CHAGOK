"""
SQLAlchemy Base and helper utilities
"""

from sqlalchemy import Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Helper for str-based enums to use value instead of name in PostgreSQL
def StrEnumColumn(enum_class, **kwargs):
    """Create SQLEnum column that uses enum values (lowercase) instead of names (uppercase)."""
    return SQLEnum(enum_class, values_callable=lambda x: [e.value for e in x], **kwargs)
