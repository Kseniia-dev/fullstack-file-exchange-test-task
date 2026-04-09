from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.alerts import router as alerts_router
from src.api.routes.files import router as files_router
from src.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title="File Exchange MVP")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(files_router)
    application.include_router(alerts_router)
    return application


app = create_app()
