from pathlib import Path
import mimetypes
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from app import models
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.schemas import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
    ApplicationDocumentResponse,
    DocumentType,
)

Base.metadata.create_all(bind=engine)

UPLOAD_ROOT = Path("uploaded_documents")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title = "Job Application Tracker API",
    description = "An API for tracking job applications, including companies, positions, and application statuses.",
    version = "0.1.0"
)

@app.get("/")
def home():
    return {"message": "Welcome to the Job Application Tracker API!",
            "status": "API is running successfully."
            }

@app.get("/health")
def health_check():
    return {"status": "ok",
             "message": "API is healthy and responsive."}

@app.get("/status")
def get_status():
    return {
        "checking_self": 200,
        "checking_database": 200,
        "checking_external_services": 200,
        "overall_status": "ok"
    }


applications = [
    {
        "id": 1,
        "company": "BMW",
        "position": "Working Student Cloud Data",
        "status": "Applied",
        "German_required": False
    },
    {
        "id": 2,
        "company": "Bosch",
        "position": "Internship IT Project Management",
        "status": "Preparing",
        "German_required": True
    },
    {
        "id": 1000,
        "company": "Easter Egg Company",
        "position": "Easter Egg Position",
        "status": "This is an Easter egg. Not a real application. don't take it seriously.",
        "German_required": False
    }

]


@app.get("/applications", response_model=list[JobApplicationResponse])
def get_applications(
    status: str | None = None,
    company: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Application)

    if status is not None:
        query = query.filter(models.Application.status == status)

    if company is not None:
        query = query.filter(models.Application.company == company)

    return query.all()

@app.get("/applications/{application_id}", response_model=JobApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return application



@app.post("/applications", response_model=JobApplicationResponse)
def create_application(application: JobApplicationCreate, db: Session = Depends(get_db)):
    db_application = models.Application(
        company=application.company,
        position=application.position,
        status=application.status,
        german_required=application.german_required,
        location=application.location,
        notes=application.notes,
        job_link=application.job_link
    )

    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return db_application


@app.post(
    "/applications/{application_id}/documents",
    response_model=ApplicationDocumentResponse,
    status_code=201
)
async def upload_application_document(
    application_id: int,
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    safe_file_name = Path(file.filename).name
    application_folder = UPLOAD_ROOT / f"application_{application_id}"
    application_folder.mkdir(parents=True, exist_ok=True)

    stored_file_name = f"{uuid4().hex}_{safe_file_name}"
    stored_file_path = application_folder / stored_file_name

    file_contents = await file.read()
    stored_file_path.write_bytes(file_contents)

    db_document = models.ApplicationDocument(
        application_id=application_id,
        document_type=document_type,
        file_name=safe_file_name,
        file_path=str(stored_file_path),
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


@app.get("/documents/{document_id}/file")
def serve_document_file(document_id: int, download: bool = Query(False), db: Session = Depends(get_db)):
    doc = db.query(models.ApplicationDocument).filter(
        models.ApplicationDocument.id == document_id
    ).first()

    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    stored_path = Path(doc.file_path)

    try:
        stored_resolved = stored_path.resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file path")

    upload_root_resolved = UPLOAD_ROOT.resolve()

    if not str(stored_resolved).startswith(str(upload_root_resolved)):
        raise HTTPException(status_code=403, detail="Access denied")

    if not stored_resolved.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    mime_type, _ = mimetypes.guess_type(doc.file_name)
    if mime_type is None:
        mime_type = "application/octet-stream"

    disposition = f'attachment; filename="{doc.file_name}"' if download else f'inline; filename="{doc.file_name}"'
    headers = {"Content-Disposition": disposition}

    return FileResponse(path=stored_resolved, media_type=mime_type, headers=headers)

@app.delete("/applications/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(application)
    db.commit()

    return {
        "message": "Application deleted successfully",
        "deleted_application_id": application_id
    }

@app.put("/applications/{application_id}", response_model=JobApplicationResponse)
def update_application(
    application_id: int,
    updated_application: JobApplicationCreate,
    db: Session = Depends(get_db)
):
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    application.company = updated_application.company
    application.position = updated_application.position
    application.status = updated_application.status
    application.german_required = updated_application.german_required
    application.location = updated_application.location
    application.notes = updated_application.notes
    application.job_link = updated_application.job_link

    db.commit()
    db.refresh(application)

    return application


@app.patch("/applications/{application_id}", response_model=JobApplicationResponse)
def partially_update_application(
    application_id: int,
    updated_fields: JobApplicationUpdate,
    db: Session = Depends(get_db)
):
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = updated_fields.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(application, key, value)

    db.commit()
    db.refresh(application)

    return application
