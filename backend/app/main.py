from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_connections,
    routes_history,
    routes_models,
    routes_query,
    routes_schema,
)
from app.config import get_settings
from app.storage.app_store import init_db

app = FastAPI(title="QueryFlow API")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(routes_connections.router)
app.include_router(routes_schema.router)
app.include_router(routes_query.router)
app.include_router(routes_history.router)
app.include_router(routes_models.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
