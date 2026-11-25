from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import audits, contracts, invoices
from app.schemas import HealthResponse
from app.seed import seed


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed()
    yield


app = FastAPI(
    title="FreightProof API",
    description="Deterministic freight invoice auditing",
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

app.include_router(invoices.router, prefix="/api/v1")
app.include_router(audits.router, prefix="/api/v1")
app.include_router(contracts.router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="freightproof-api")


@app.get("/api/v1/health", response_model=HealthResponse)
def health_v1() -> HealthResponse:
    return HealthResponse(status="ok", service="freightproof-api")