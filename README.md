# Job Application Tracker API

A RESTful API for tracking job applications, built with FastAPI, SQLite, SQLAlchemy, and Pydantic.

## Project Overview

This project helps manage job applications by storing company names, positions, application status, German language requirement, location, notes, uploaded documents, and creation time.

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
- Upload the CV, cover letter, and additional documents used for each application
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

You can also upload documents for a saved application with `POST /applications/{application_id}/documents` using `multipart/form-data` with:

- `document_type`: `CV`, `Cover Letter`, or `Additional`
- `file`: the document file itself


**Documents & Previews**

- **Upload endpoint:** `POST /applications/{application_id}/documents` accepts `multipart/form-data` with `document_type` and `file` (the uploaded file will be stored on disk).
- **Storage location:** uploaded files are saved under `uploaded_documents/application_<id>/` with a generated filename. The original filename and metadata are stored in the database.
- **Serve endpoint:** `GET /documents/{document_id}/file` serves the stored file with a proper `Content-Type` header. By default the endpoint sets `Content-Disposition: inline` so browsers will open PDFs in a new tab (images display inline).
- **Force download:** append `?download=true` to the serve URL to force `Content-Disposition: attachment` and prompt a download.
- **Preview behavior:** Some browsers (notably Chrome) block base64-embedded PDF iframes; to avoid this the dashboard opens PDFs via the backend serve URL in a new tab rather than embedding them.

Note: the local uploads folder and local SQLite DB are intentionally ignored by Git (see `.gitignore`) so uploaded files and the database are not committed to the repository.

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

Run the Streamlit dashboard (optional):

```powershell
streamlit run streamlit_app/dashboard.py
```

## Setup & Run (Detailed)

These steps help contributors run the project in a reproducible environment. Pick either Conda or a Python virtual environment (`venv`).

### Option A — Conda (recommended)

```powershell
conda create -n job-tracker-api python=3.11 -y
conda activate job-tracker-api
pip install -r requirements.txt
```

### Option B — venv (native Python)

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Windows cmd
.\.venv\Scripts\activate.bat
# Unix / macOS
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the backend API

```powershell
# from project root
python -m uvicorn app.main:app --reload
```

Open docs at: `http://127.0.0.1:8000/docs`

### Run the Streamlit dashboard (optional)

```powershell
streamlit run streamlit_app/dashboard.py
```

### Example: upload a document (curl)

Replace `{application_id}` with an existing application ID and update the file path.

```bash
curl -X POST \
  -F "document_type=CV" \
  -F "file=@/path/to/your/CV.pdf" \
  http://127.0.0.1:8000/applications/{application_id}/documents
```

### View or open uploaded files

- Serve URL: `GET /documents/{document_id}/file`
- Open in browser (inline): request without query param — the API returns `Content-Disposition: inline` so PDFs open in a new tab.
- Force download: append `?download=true` to force `Content-Disposition: attachment`.

### Notes & Troubleshooting

- Uploaded files are stored under `uploaded_documents/application_<id>/`. The original filename and metadata are stored in the DB.
- The project intentionally ignores the uploads folder and local SQLite DB in `.gitignore`. Do not commit these files.
- If PDFs do not render inline, try the `?download=true` option or open the link directly in a browser tab.
- If the backend is not reachable, confirm `uvicorn` is running and `API_URL` in `streamlit_app/dashboard.py` points to `http://127.0.0.1:8000`.

```

## Future Improvements

- Add Streamlit dashboard
- Add authentication
- Add CSV export
- Add application deadline reminders
- Add GitHub Actions workflow
- Deploy API to Azure