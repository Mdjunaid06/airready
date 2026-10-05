"""FastAPI app instance and one-time model startup loading."""
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import fleet

model_registry = {"bundle": None, "engines": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_registry["bundle"] = joblib.load(settings.model_path)
    from app.routers.fleet import build_engine_predictions

    model_registry["engines"] = build_engine_predictions(model_registry["bundle"])
    yield
    model_registry["bundle"] = None
    model_registry["engines"] = None


app = FastAPI(
    title="AirReady API",
    description="Predictive maintenance & fleet availability API — SIH 2026 PS 26249",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fleet.router, tags=["fleet"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
