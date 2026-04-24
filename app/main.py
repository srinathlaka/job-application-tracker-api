
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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

@app.get("/applications")
def get_applications():
    return applications

@app.get("/applications/{application_id}")
def get_application(application_id: int):
    for application in applications:
        if application["id"] == application_id:
            return application
        elif application["id"] == application_id:
            return application
    raise HTTPException(status_code=404, detail="Application not found")


class JobApplication(BaseModel):
    id: int
    company: str
    position: str
    status: str
    german_required: bool


@app.post("/applications")
def create_application(application: JobApplication):
    applications.append(application.dict())
    return {
        "message": "Application added successfully",
        "application": application.dict()
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

    return {
        "error": "Application not found"
    }

@app.put("/applications/{application_id}")
def update_application(application_id: int, updated_application: JobApplication):
    for index, application in enumerate(applications):
        if application["id"] == application_id:
            applications[index] = updated_application.dict()
            return {
                "message": "Application updated successfully",
                "application": updated_application.dict()
            }

    return {
        "error": "Application not found"
    }

