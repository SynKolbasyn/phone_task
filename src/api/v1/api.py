from fastapi import APIRouter

from api.v1.calls import router as calls_router

api_router = APIRouter(prefix="/v1")
api_router.include_router(calls_router)
