conda activate job-tracker-api

Start-Process powershell -ArgumentList "python -m uvicorn app.main:app --reload"

Start-Process powershell -ArgumentList "streamlit run streamlit_app/dashboard.py"