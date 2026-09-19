import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile
)

from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import PotholeReport
from .schemas import PotholeReportResponse
from .detector import detect_pothole


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


UPLOAD_FOLDER = "uploads"

ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/jpg"
]


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# CREATE REPORT WITH IMAGE

@router.post("/", response_model=PotholeReportResponse)
def create_report(
    image: UploadFile = File(...),
    description: str = Form(...),
    severity: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    db: Session = Depends(get_db)
):

    # Check image type
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are allowed"
        )

    # Create uploads folder if it doesn't exist
    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    # Get image extension
    file_extension = os.path.splitext(
        image.filename
    )[1]

    # Create unique filename
    unique_filename = (
        f"{uuid.uuid4()}{file_extension}"
    )

    # Create full file path
    file_path = os.path.join(
        UPLOAD_FOLDER,
        unique_filename
    )

    # Save image
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            image.file,
            buffer
        )

    # Create database report
    new_report = PotholeReport(
        image_path=file_path,
        description=description,
        severity=severity,
        latitude=latitude,
        longitude=longitude,
        confidence=detect_pothole(file_path),
        status="pending"
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report


# GET ALL REPORTS

@router.get(
    "/",
    response_model=list[PotholeReportResponse]
)
def get_reports(
    db: Session = Depends(get_db)
):

    reports = db.query(
        PotholeReport
    ).all()

    return reports


# GET SINGLE REPORT

@router.get(
    "/{report_id}",
    response_model=PotholeReportResponse
)
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):

    report = db.query(
        PotholeReport
    ).filter(
        PotholeReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report


# UPDATE REPORT STATUS

@router.put(
    "/{report_id}/status",
    response_model=PotholeReportResponse
)
def update_report_status(
    report_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    report = db.query(
        PotholeReport
    ).filter(
        PotholeReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    report.status = status

    db.commit()
    db.refresh(report)

    return report


# DELETE REPORT

@router.delete(
    "/{report_id}"
)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):

    report = db.query(
        PotholeReport
    ).filter(
        PotholeReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    db.delete(report)
    db.commit()

    return {
        "message": "Report deleted successfully"
    }