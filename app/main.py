
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from app import models
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends
from app.database import engine, Base, SessionLocal
from app.schemas import JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse

Base.metadata.create_all(bind=engine)

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
