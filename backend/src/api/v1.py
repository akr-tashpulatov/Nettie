# api/v1/__init__.py
from fastapi import APIRouter

from src.modules.analytics.api.router import router as analytics_router
from src.modules.audit.api.router import router as audit_router
from src.modules.auth.api.router import router as auth_router
from src.modules.media.api.router import router as media_router
from src.modules.renewal_settings.api.router import router as renewal_settings_router
from src.modules.speaking.api.router import router as speaking_router
from src.modules.speaking_session.api.router import router as speaking_session_router
from src.modules.study_group.api.router import router as study_group_router
from src.modules.subscription.api.router import router as subscription_router
from src.modules.tariff.api.router import router as tariff_router
from src.modules.transaction.api.router import router as transactions_router
from src.modules.user.api.router import router as user_router
from src.modules.webhook.api.router import router as webhook_router
from src.modules.writing_catalog.api.router import router as writing_catalog_router
from src.modules.writing_session.api.router import router as writing_session_router

api_v1 = APIRouter(prefix="/v1")

api_v1.include_router(auth_router)
api_v1.include_router(analytics_router)
api_v1.include_router(user_router)
api_v1.include_router(tariff_router)
api_v1.include_router(renewal_settings_router)
api_v1.include_router(study_group_router)
api_v1.include_router(subscription_router)
api_v1.include_router(transactions_router)
api_v1.include_router(audit_router)
api_v1.include_router(webhook_router)
api_v1.include_router(speaking_router)
api_v1.include_router(speaking_session_router)
api_v1.include_router(media_router)
api_v1.include_router(writing_catalog_router)
api_v1.include_router(writing_session_router)
