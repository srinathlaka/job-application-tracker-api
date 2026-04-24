
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from app.database import engine, Base
from app import models

Base.metadata.create_all(bind=engine)

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

ApplicationStatus = Literal[
    "Preparing",
    "Applied",
    "Interview Scheduled",
    "Rejected",
    "Accepted"
]

@app.get("/applications")
def get_applications(status: str | None = None, company: str | None = None):
    filtered_applications = applications

    if status is not None:
        filtered_applications = [
            application for application in filtered_applications
            if application["status"].lower() == status.lower()
        ]

    if company is not None:
        filtered_applications = [
            application for application in filtered_applications
            if application["company"].lower() == company.lower()
        ]

    return filtered_applications

@app.get("/applications/{application_id}")
def get_application(application_id: int):
    for application in applications:
        if application["id"] == application_id:
            return application
    raise HTTPException(status_code=404, detail="Application not found")


class JobApplication(BaseModel):
    id: int
    company: str
    position: str
    status: ApplicationStatus
    german_required: bool
    location: str | None = None
    notes: str | None = None


class JobApplicationCreate(BaseModel):
    company: str
    position: str
    status: ApplicationStatus
    german_required: bool
    location: str | None = None
    notes: str | None = None

class JobApplicationUpdate(BaseModel):
    company: str | None = None
    position: str | None = None
    status: ApplicationStatus | None = None
    german_required: bool | None = None
    location: str | None = None
    notes: str | None = None

@app.post("/applications")
def create_application(application: JobApplicationCreate):
    new_id = max([application["id"] for application in applications], default=0) + 1

    new_application = {
        "id": new_id,
        **application.dict()
    }

    applications.append(new_application)

    return {
        "message": "Application added successfully",
        "application": new_application
    }

@app.delete("/applications/{application_id}")
def delete_application(application_id: int):
    for application in applications:
        if application["id"] == application_id:
            applications.remove(application)
            return {
                "message": "Application deleted successfully",
                "deleted_application": application
            }

    raise HTTPException(status_code=404, detail="Application not found")

@app.put("/applications/{application_id}")
def update_application(application_id: int, updated_application: JobApplication):
    for index, application in enumerate(applications):
        if application["id"] == application_id:
            applications[index] = updated_application.dict()
            return {
                "message": "Application updated successfully",
                "application": updated_application.dict()
            }

    raise HTTPException(status_code=404, detail="Application not found")


@app.patch("/applications/{application_id}")
def partially_update_application(application_id: int, updated_fields: JobApplicationUpdate):
    for application in applications:
        if application["id"] == application_id:
            update_data = updated_fields.dict(exclude_unset=True)

            application.update(update_data)

            return {
                "message": "Application updated successfully",
                "application": application
            }

    raise HTTPException(status_code=404, detail="Application not found")

