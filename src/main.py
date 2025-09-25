from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from api.v1.api import api_router
from core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="Phone Call Service",
    description="A service for managing phone calls and recordings.",
    version="0.1.0",
)

# Настройка CORS (на всякий случай)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(api_router)


@app.get("/health")
async def health_check() -> Response:
    return Response()
