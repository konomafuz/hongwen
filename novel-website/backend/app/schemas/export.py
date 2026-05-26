from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    project_id: int
    format: str = Field(default="word", pattern="^(word|epub)$")
    include_outline: bool = True


class ExportResponse(BaseModel):
    download_url: str
    filename: str