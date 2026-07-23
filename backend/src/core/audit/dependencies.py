from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session

from .logger import IAuditLogger
from .sqlalchemy_logger import SQLAlchemyAuditLogger


def get_audit_logger(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IAuditLogger:
    return SQLAlchemyAuditLogger(session)
