import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

STATUS_OPTIONS = [
    "Preparing",
    "Applied",
    "Interview Scheduled",
    "Rejected",
    "Accepted"
]

st.set_page_config(
    page_title="Job Application Tracker",
    layout="wide"
)


def load_applications(status=None, company=None):
    params = {}

    if status and status != "All":
        params["status"] = status

    if company and company.strip():
        params["company"] = company.strip()

    try:
        response = requests.get(f"{API_URL}/applications", params=params)

        if response.status_code == 200:
            return response.json()

        st.error("Failed to load applications from the API.")
        return []

    except requests.exceptions.ConnectionError:
        st.error(
            "FastAPI backend is not running. "
            "Start it with: python -m uvicorn app.main:app --reload"
        )
        return []


def create_application(application_data):
    try:
        response = requests.post(
            f"{API_URL}/applications",
            json=application_data
        )
        return response

    except requests.exceptions.ConnectionError:
        st.error("FastAPI backend is not running.")
        return None


def update_application_status(application_id, new_status):
    try:
        response = requests.patch(
            f"{API_URL}/applications/{application_id}",
            json={"status": new_status}
        )
        return response

    except requests.exceptions.ConnectionError:
        st.error("FastAPI backend is not running.")
        return None


def update_application_notes(application_id, new_notes):
    try:
        response = requests.patch(
            f"{API_URL}/applications/{application_id}",
            json={"notes": new_notes}
        )
        return response

    except requests.exceptions.ConnectionError:
        st.error("FastAPI backend is not running.")
        return None


def delete_application(application_id):
    try:
        response = requests.delete(
            f"{API_URL}/applications/{application_id}"
        )
        return response

    except requests.exceptions.ConnectionError:
        st.error("FastAPI backend is not running.")
        return None


st.title("Job Application Tracker")
st.caption("A Streamlit dashboard connected to a FastAPI backend and SQLite database.")

st.divider()

with st.sidebar:
    st.header("Filters")

    selected_status = st.selectbox(
        "Application status",
        ["All"] + STATUS_OPTIONS
    )

    company_filter = st.text_input("Company name")

    st.divider()

    if st.button("Refresh data", use_container_width=True):
        st.rerun()


applications = load_applications(
    status=selected_status,
    company=company_filter
)

total_applications = len(applications)
applied_count = sum(1 for app in applications if app["status"] == "Applied")
interview_count = sum(1 for app in applications if app["status"] == "Interview Scheduled")
rejected_count = sum(1 for app in applications if app["status"] == "Rejected")

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric("Total", total_applications)

with metric_col2:
    st.metric("Applied", applied_count)

with metric_col3:
    st.metric("Interviews", interview_count)

with metric_col4:
    st.metric("Rejected", rejected_count)

st.divider()

left_col, right_col = st.columns([1.1, 1])

with left_col:
    st.subheader("Add new application")

    with st.form("add_application_form", clear_on_submit=True):
        company = st.text_input("Company *")
        position = st.text_input("Position *")

        input_col1, input_col2 = st.columns(2)

        with input_col1:
            status = st.selectbox("Status", STATUS_OPTIONS)

        with input_col2:
            german_required = st.checkbox("German required")

        location = st.text_input("Location")
        notes = st.text_area("Notes")
        job_link = st.text_input("Job ad link")
        st.warning("Optional: Add the original job ad link so you can reopen it later for interview preparation.")

        submitted = st.form_submit_button("Add application", use_container_width=True)

        if submitted:
            if not company.strip():
                st.error("Company name is required.")
            elif not position.strip():
                st.error("Position is required.")
            else:
                new_application = {
                    "company": company.strip(),
                    "position": position.strip(),
                    "status": status,
                    "german_required": german_required,
                    "location": location.strip() if location.strip() else None,
                    "notes": notes.strip() if notes.strip() else None,
                    "job_link": job_link.strip() if job_link.strip() else None
                }

                response = create_application(new_application)

                if response and response.status_code == 200:
                    st.success("Application added successfully.")
                    st.rerun()
                elif response:
                    st.error(f"Failed to add application. Status code: {response.status_code}")

with right_col:
    st.subheader("Update application")

    if applications:
        application_options = {
            f'{app["id"]} | {app["company"]} | {app["position"]}': app["id"]
            for app in applications
        }

        selected_application = st.selectbox(
            "Select application",
            list(application_options.keys())
        )

        with st.container(border=True):
            st.markdown("**Update status**")

            new_status = st.selectbox(
                "New status",
                STATUS_OPTIONS,
                key="update_status_selectbox"
            )

            if st.button("Update status", use_container_width=True):
                selected_application_id = application_options[selected_application]

                response = update_application_status(
                    selected_application_id,
                    new_status
                )

                if response and response.status_code == 200:
                    st.success("Status updated successfully.")
                    st.rerun()
                elif response:
                    st.error(f"Failed to update status. Status code: {response.status_code}")

        with st.container(border=True):
            st.markdown("**Update notes**")

            new_notes = st.text_area("New notes", key="update_notes_textarea")

            if st.button("Update notes", use_container_width=True):
                selected_application_id = application_options[selected_application]

                response = update_application_notes(
                    selected_application_id,
                    new_notes.strip() if new_notes.strip() else None
                )

                if response and response.status_code == 200:
                    st.success("Notes updated successfully.")
                    st.rerun()
                elif response:
                    st.error(f"Failed to update notes. Status code: {response.status_code}")

        with st.container(border=True):
            st.markdown("**Delete application**")

            st.warning("This action will permanently delete the selected application.")

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this application",
                key="confirm_delete_checkbox"
            )

            if st.button("Delete application", use_container_width=True):
                if not confirm_delete:
                    st.error("Please confirm before deleting.")
                else:
                    selected_application_id = application_options[selected_application]

                    response = delete_application(selected_application_id)

                    if response and response.status_code == 200:
                        st.success("Application deleted successfully.")
                        st.rerun()
                    elif response:
                        st.error(f"Failed to delete application. Status code: {response.status_code}")

    else:
        st.info("No applications available to update.")

st.divider()

header_col1, header_col2 = st.columns([2, 1])

with header_col1:
    st.subheader("Applications")

with header_col2:
    st.caption(
        f"Status: {selected_status} | "
        f"Company: {company_filter if company_filter else 'All'}"
    )

if applications:
    applications_df = pd.DataFrame(applications)

    csv_data = applications_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download applications as CSV",
        data=csv_data,
        file_name="job_applications.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.dataframe(
        applications,
        use_container_width=True,
        hide_index=True,
        column_order=[
            "id",
            "company",
            "position",
            "status",
            "german_required",
            "location",
            "job_link",
            "notes",
            "created_at"
        ]
    )
else:
    st.info("No applications found for the selected filters.")