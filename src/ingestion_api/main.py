from fastapi import FastAPI

from src.ingestion_api.config import settings
from src.ingestion_api.database import Base, engine
from src.ingestion_api.routes.auth import router as auth_router
from src.ingestion_api.routes.ingestion import router as ingestion_router
from src.ingestion_api.routes.prediction import router as prediction_router
from src.ingestion_api.routes.users import router as users_router

app = FastAPI(title=settings.app_name)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(ingestion_router, prefix=settings.api_prefix)
app.include_router(prediction_router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
