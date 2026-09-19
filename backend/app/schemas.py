from datetime import datetime

from pydantic import BaseModel, Field


class PotholeReportCreate(BaseModel):

    description: str | None = None

    severity: str = Field(
        default="medium"
    )

    latitude: float = Field(
        ...,
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180
    )


class PotholeReportResponse(BaseModel):

    id: int

    image_path: str

    description: str | None

    severity: str

    latitude: float | None

    longitude: float | None

    confidence: float

    status: str

    created_at: datetime

    class Config:
        from_attributes = True