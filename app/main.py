from typing import Any, AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.config import settings
from core.db_helper import db_helper
from core.models import Base
from api import router as api_router
from core.admin.service import admin_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with db_helper.session_factory() as session:  # Создаем администратора
        await admin_service.create_admin(session=session)

    yield


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,  # Ускоряет работу с сериализацией и десериализацией
)
app.include_router(router=api_router, prefix=settings.api.prefix)


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker healthcheck"""
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
