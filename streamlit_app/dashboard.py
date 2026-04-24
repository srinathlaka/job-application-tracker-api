import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Job Application Tracker")
st.caption("Streamlit frontend connected to FastAPI backend and SQLite database.")

st.divider()


def load_applications(status=None, company=None):
    params = {}

    if status and status != "All":
        params["status"] = status

    if company:
        params["company"] = company

    response = requests.get(f"{API_URL}/applications", params=params)

    if response.status_code == 200:
        return response.json()

    st.error("Failed to load applications from the API.")
    return []


with st.sidebar:
    st.header("Filters")

    selected_status = st.selectbox(
        "Application Status",
        ["All", "Preparing", "Applied", "Interview Scheduled", "Rejected", "Accepted"]
    )

    company_filter = st.text_input("Company name")

    st.divider()

    refresh_button = st.button("Refresh Data", use_container_width=True)


applications = load_applications(
    status=selected_status,
    company=company_filter
)

total_applications = len(applications)
applied_count = sum(1 for app in applications if app["status"] == "Applied")
interview_count = sum(1 for app in applications if app["status"] == "Interview Scheduled")
rejected_count = sum(1 for app in applications if app["status"] == "Rejected")

col1, col2, col3, col4 = st.columns(4)

st.subheader("Add New Application")

with st.form("add_application_form"):
    company = st.text_input("Company")
    position = st.text_input("Position")

    status = st.selectbox(
        "Status",
        ["Preparing", "Applied", "Interview Scheduled", "Rejected", "Accepted"]
    )

    german_required = st.checkbox("German required")
    location = st.text_input("Location")
    notes = st.text_area("Notes")

    submitted = st.form_submit_button("Add Application")

    if submitted:
        new_application = {
            "company": company,
            "position": position,
            "status": status,
            "german_required": german_required,
            "location": location if location else None,
            "notes": notes if notes else None
        }

        response = requests.post(
            f"{API_URL}/applications",
            json=new_application
        )

        if response.status_code == 200:
            st.success("Application added successfully.")
            st.rerun()
        else:
            st.error("Failed to add application.")

with col1:
    st.metric("Total Applications", total_applications)

with col2:
    st.metric("Applied", applied_count)

with col3:
    st.metric("Interviews", interview_count)

with col4:
    st.metric("Rejected", rejected_count)

st.divider()

st.subheader("Applications")

if applications:
    st.dataframe(
        applications,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No applications found for the selected filters.")