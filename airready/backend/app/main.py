"""
FastAPI app instance. See docs/BACKEND.md for conventions.

Model loading: currently a no-op placeholder (see TODO below) because the fleet
router serves demo data until Day 2's real model integration — see
docs/ARCHITECTURE.md Section 2 for why these layers are deliberately decoupled.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import fleet

model_registry = {"model": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO (Day 2): load the real trained model here, once ml/src/train.py has
    # produced ml/models/rul_model.pkl. Example:
    #
    #   import joblib
    #   model_registry["model"] = joblib.load(settings.model_path)
    #
    # Keep this load in app startup (not per-request) — see docs/BACKEND.md
    # Section 3 on why the model must be loaded once, not reloaded per call.
    yield
    model_registry["model"] = None


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
