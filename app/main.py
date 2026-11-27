from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, games, family, profiles, scores, health
from fastapi.staticfiles import StaticFiles
import os

os.makedirs("/app/uploads", exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    description="API de jogos cognitivos para idosos",
    version="1.0.0",
    # A documentação mostra todas as rotas da API: só fica aberta em desenvolvimento.
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
)

app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth.router, prefix="/api")
app.include_router(games.router, prefix="/api")
app.include_router(family.router, prefix="/api")
app.include_router(profiles.router, prefix="/api")
app.include_router(scores.router, prefix="/api")
app.include_router(health.router, prefix="/api")


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok", "app": settings.APP_NAME}