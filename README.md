# Job Application Tracker API

A RESTful API for tracking job applications, built with FastAPI, SQLite, SQLAlchemy, and Pydantic.

## Project Overview

This project helps manage job applications by storing company names, positions, application status, German language requirement, location, notes, and creation time.

The main goal of this project is to learn RESTful API development using Python and FastAPI while building a useful job tracking tool.

## Tech Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- Uvicorn

## Features

- Create a new job application
- View all job applications
- View one application by ID
- Update a full application
- Partially update selected fields
- Delete an application
- Filter applications by status and company
- Validate allowed application statuses
- Store data permanently using SQLite
- Automatically generate ID and creation timestamp

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome endpoint |
| GET | `/status` | API status check |
| GET | `/applications` | Get all applications |
| GET | `/applications/{application_id}` | Get one application by ID |
| POST | `/applications` | Create a new application |
| PUT | `/applications/{application_id}` | Fully update an application |
| PATCH | `/applications/{application_id}` | Partially update an application |
| DELETE | `/applications/{application_id}` | Delete an application |

## Example Request Body

```json
{
  "company": "BMW",
  "position": "Student Trainee Cloud Data",
  "status": "Applied",
  "german_required": true,
  "location": "Munich",
  "notes": "Prepare cloud and Power BI questions"
}
```

## Allowed Status Values

```text
Preparing
Applied
Interview Scheduled
Rejected
Accepted
```

## Run Locally

Create and activate the Conda environment:

```powershell
conda create -n job-tracker-api python=3.11
conda activate job-tracker-api
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the FastAPI server:

```powershell
python -m uvicorn app.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## Future Improvements

- Add Streamlit dashboard
- Add authentication
- Add CSV export
- Add application deadline reminders
- Add GitHub Actions workflow
- Deploy API to Azure