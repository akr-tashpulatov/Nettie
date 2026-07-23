from fastapi import APIRouter

from src.modules.auth.api.router import router as auth_router
from src.modules.exam.api.router import router as exam_router
from src.modules.media.api.router import router as media_router
from src.modules.test.api.router import router as test_router
from src.modules.user.api.router import router as user_router

api_v1 = APIRouter(prefix="/v1")

api_v1.include_router(auth_router)
api_v1.include_router(user_router)
api_v1.include_router(media_router)
api_v1.include_router(test_router)
api_v1.include_router(exam_router)
