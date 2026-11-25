from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = "audio/wav"


class RunCreateRequest(BaseModel):
    audio_s3_key: str
    reference_transcript: str
    selected_stacks: list[str] = Field(min_length=1)


class RunCreateResponse(BaseModel):
    run_id: str
    status: str
    created_at: str
