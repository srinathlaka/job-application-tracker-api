from pathlib import Path

import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 8

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
        response = requests.get(
            f"{API_URL}/applications",
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            return response.json()

        st.error("Failed to load applications from the API.")
        return []

    except requests.exceptions.RequestException:
        st.error(
            "FastAPI backend is not running. "
            "Start it with: python -m uvicorn app.main:app --reload"
        )
        return []


def create_application(application_data):
    try:
        response = requests.post(
            f"{API_URL}/applications",
            json=application_data,
            timeout=REQUEST_TIMEOUT
        )
        return response

    except requests.exceptions.RequestException:
        st.error("FastAPI backend is not running.")
        return None


def upload_application_document(application_id, document_type, uploaded_file):
    if uploaded_file is None:
        return None

    try:
        response = requests.post(
            f"{API_URL}/applications/{application_id}/documents",
            data={"document_type": document_type},
            timeout=REQUEST_TIMEOUT,
            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type or "application/octet-stream"
                )
            }
        )
        return response

    except requests.exceptions.RequestException:
        st.error("FastAPI backend is not running.")
        return None


def is_image_document(file_name):
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    file_name_lower = file_name.lower()
    return any(file_name_lower.endswith(extension) for extension in image_extensions)


def is_pdf_document(file_name):
    return file_name.lower().endswith(".pdf")


def get_document_mime_type(file_name):
    file_name_lower = file_name.lower()

    if file_name_lower.endswith(".pdf"):
        return "application/pdf"
    if file_name_lower.endswith(".png"):
        return "image/png"
    if file_name_lower.endswith(".jpg") or file_name_lower.endswith(".jpeg"):
        return "image/jpeg"
    if file_name_lower.endswith(".gif"):
        return "image/gif"
    if file_name_lower.endswith(".webp"):
        return "image/webp"

    return "application/octet-stream"


def render_pdf_preview(file_path, file_name):
    # Inline PDF previews via base64 were blocked by some browsers (Chrome).
    # We now serve PDFs via the backend and open them in a new tab instead.
    st.info("PDFs open in a new tab. Use the link below to view the document.")


def render_document_actions(document):
    file_path = document.get("file_path")
    file_name = document["file_name"]

    if not file_path:
        st.caption("No saved path available")
        return

    path = Path(file_path)

    if not path.exists():
        st.warning("Saved file no longer exists on disk.")
        return

    download_bytes = path.read_bytes()

    st.download_button(
        label=f"Download {file_name}",
        data=download_bytes,
        file_name=file_name,
        mime=get_document_mime_type(file_name),
        use_container_width=True,
        key=f"download_{document['id']}"
    )

    if is_image_document(file_name):
        st.image(file_path, caption=file_name, use_container_width=True)
    elif is_pdf_document(file_name):
        url_view = f"{API_URL}/documents/{document['id']}/file"
        url_download = f"{API_URL}/documents/{document['id']}/file?download=true"
        st.markdown(
            f'<a href="{url_view}" target="_blank">Open {file_name} in new tab</a> '
            f'| <a href="{url_download}" target="_blank">Open as download</a>',
            unsafe_allow_html=True,
        )
    else:
        st.caption(file_path)


def update_application_status(application_id, new_status):
    try:
        response = requests.patch(
            f"{API_URL}/applications/{application_id}",
            json={"status": new_status},
            timeout=REQUEST_TIMEOUT
        )
        return response

    except requests.exceptions.RequestException:
        st.error("FastAPI backend is not running.")
        return None


def update_application_notes(application_id, new_notes):
    try:
        response = requests.patch(
            f"{API_URL}/applications/{application_id}",
            json={"notes": new_notes},
            timeout=REQUEST_TIMEOUT
        )
        return response

    except requests.exceptions.RequestException:
        st.error("FastAPI backend is not running.")
        return None


def delete_application(application_id):
    try:
        response = requests.delete(
            f"{API_URL}/applications/{application_id}",
            timeout=REQUEST_TIMEOUT
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
        job_link = st.text_input("Job ad link")
        st.caption(
            "Optional: Add the original job ad link so you can reopen it later for interview preparation."
        )

        notes = st.text_area("Notes")
        cv_file = st.file_uploader("CV", type=["pdf", "doc", "docx"], key="cv_file")
        cover_letter_file = st.file_uploader(
            "Cover letter",
            type=["pdf", "doc", "docx"],
            key="cover_letter_file"
        )
        additional_files = st.file_uploader(
            "Additional documents",
            type=["pdf", "doc", "docx", "txt", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="additional_files"
        )
        st.caption(
            "Upload the exact CV and cover letter version you send, plus any supporting files like portfolio, transcript, or certificates."
        )

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
                    "job_link": job_link.strip() if job_link.strip() else None,
                    "notes": notes.strip() if notes.strip() else None
                }

                response = create_application(new_application)

                if response and response.status_code == 200:
                    application_id = response.json()["id"]
                    upload_failures = []

                    for document_type, uploaded_file in [
                        ("CV", cv_file),
                        ("Cover Letter", cover_letter_file),
                    ]:
                        if uploaded_file is None:
                            continue

                        document_response = upload_application_document(
                            application_id,
                            document_type,
                            uploaded_file
                        )

                        if not document_response or document_response.status_code != 201:
                            upload_failures.append(document_type)

                    for uploaded_file in additional_files or []:
                        document_response = upload_application_document(
                            application_id,
                            "Additional",
                            uploaded_file
                        )

                        if not document_response or document_response.status_code != 201:
                            upload_failures.append(uploaded_file.name)

                    if upload_failures:
                        st.warning(
                            "Application saved, but some documents failed to upload: "
                            + ", ".join(upload_failures)
                        )
                    else:
                        st.success("Application and documents added successfully.")

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
    st.subheader("Selected application details")

    detail_options = {
        f'{app["id"]} | {app["company"]} | {app["position"]}': app
        for app in applications
    }

    selected_detail_key = st.selectbox(
        "Select application to view details",
        list(detail_options.keys()),
        key="application_detail_selectbox"
    )

    selected_detail = detail_options[selected_detail_key]

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        st.write(f"**Company:** {selected_detail['company']}")
        st.write(f"**Position:** {selected_detail['position']}")
        st.write(f"**Status:** {selected_detail['status']}")
        st.write(f"**Location:** {selected_detail.get('location') or 'Not provided'}")

    with detail_col2:
        st.write(f"**German required:** {selected_detail['german_required']}")
        st.write(f"**Created at:** {selected_detail.get('created_at', 'Not available')}")

        if selected_detail.get("job_link"):
            st.link_button(
                "Open job ad",
                selected_detail["job_link"],
                use_container_width=True
            )
        else:
            st.info("No job ad link saved for this application.")

    if selected_detail.get("notes"):
        st.write("**Notes:**")
        st.write(selected_detail["notes"])

    documents = selected_detail.get("documents", [])

    if documents:
        st.write("**Documents used:**")

        for document in documents:
            with st.container(border=True):
                st.write(f"**{document['document_type']}**: {document['file_name']}")
                render_document_actions(document)
    else:
        st.info("No documents uploaded for this application.")

    st.divider()

    applications_for_table = [
        {key: value for key, value in app.items() if key != "documents"}
        for app in applications
    ]

    applications_df = pd.DataFrame(applications_for_table)

    csv_data = applications_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download applications as CSV",
        data=csv_data,
        file_name="job_applications.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.dataframe(
        applications_for_table,
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