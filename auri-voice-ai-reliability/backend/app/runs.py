from fastapi import APIRouter, HTTPException

from app.aws_services import create_upload_url, enqueue_run, get_run
from app.run_models import RunCreateRequest, RunCreateResponse, UploadRequest

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/uploads/presign")
def presign_upload(request: UploadRequest):
    return create_upload_url(request.filename, request.content_type)


@router.post("", response_model=RunCreateResponse)
def create_run(request: RunCreateRequest):
    item = enqueue_run(request.model_dump())
    return RunCreateResponse(
        run_id=item["run_id"],
        status=item["status"],
        created_at=item["created_at"],
    )


@router.get("/{run_id}")
def read_run(run_id: str):
    item = get_run(run_id)
    if not item:
        raise HTTPException(status_code=404, detail="Run not found")
    return item
