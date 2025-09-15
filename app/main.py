import asyncio
from typing import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from cleanup_tokens import setup_cleanup_tokens
from core.config import settings
from core.db_helper import db_helper
from core.models import Base
from api import router as api_router
from core.admin.service import admin_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with db_helper.session_factory() as session:  # Создаем администратора
        await admin_service.create_admin(session=session)

    # Запускаем cron на очистку таблицы с токенами
    cleanup_tokens_task = asyncio.create_task(setup_cleanup_tokens())
    yield

    cleanup_tokens_task.cancel()
    try:
        await cleanup_tokens_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,  # Ускоряет работу с сериализацией и десериализацией JSON
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=api_router, prefix=settings.api.prefix)


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
