from fastapi import FastAPI

from src.ingestion_api.config import settings
from src.ingestion_api.database import Base, engine
from src.ingestion_api.routes.ingestion import router as ingestion_router
from src.ingestion_api.routes.prediction import router as prediction_router

app = FastAPI(title=settings.app_name)
app.include_router(ingestion_router, prefix=settings.api_prefix)
app.include_router(prediction_router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
