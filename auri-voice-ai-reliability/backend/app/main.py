from fastapi import FastAPI

from app.config import settings
from app.runs import router as runs_router
from app.models import BenchmarkRequest, BenchmarkResponse
from app.services.benchmark import run_benchmark

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.include_router(runs_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "auri",
        "demo_mode": settings.demo_mode,
    }


@app.post("/benchmarks", response_model=BenchmarkResponse)
def create_benchmark(
    request: BenchmarkRequest,
) -> BenchmarkResponse:
    return run_benchmark(request)
