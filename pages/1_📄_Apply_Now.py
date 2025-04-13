# --- START OF FILE 1_📄_Apply_Now.py ---

import streamlit as st
import pandas as pd
from utils.helpers import initialize_session_state
from utils.agents import student_counsellor_agent
import datetime # Import datetime for default date
import os # Potentially needed if saving files locally (though not implemented here)

# Ensure state is initialized
initialize_session_state()

st.header("📄 Submit Your Application")
st.write("Please provide detailed information and upload required documents.")

# Define allowed file types and max size (for display/help text)
ALLOWED_TYPES = ["pdf", "png", "jpg", "jpeg"]
MAX_FILE_SIZE_MB = 5 # Example limit

# --- Application Form ---
with st.form("application_form"):

    # --- Personal Information ---
    st.subheader("👤 Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name*", key="apply_name")
        dob = st.date_input("Date of Birth*",
                            min_value=datetime.date(1980, 1, 1),
                            max_value=datetime.date.today() - datetime.timedelta(days=365*15), # Example: At least 15 years old
                            key="apply_dob")
    with col2:
        email = st.text_input("Email Address*", key="apply_email")
        gender = st.selectbox("Gender*", ["Select...", "Male", "Female", "Other", "Prefer not to say"], key="apply_gender")

    address = st.text_area("Permanent Address*", key="apply_address", placeholder="Enter your full permanent address")

    st.divider()

    # --- Academic Information ---
    st.subheader("📚 Academic Information")
    course = st.selectbox(
    "Select Course Applying For*",
    [
        "B.Tech Computer Science",
        "B.Tech Information Technology",
        "B.Tech Electronics and Communication",
        "B.Tech Electrical Engineering",
        "B.Tech Mechanical Engineering",
        "B.Tech Civil Engineering",
        "B.Tech Artificial Intelligence",
        "B.Tech Data Science",
        "MBA",
        "B.Sc Physics",
        "Other"
    ],
    key="apply_course"
)


    col3, col4 = st.columns(2)
    with col3:
        grade_10_percentage = st.number_input("Grade 10 Percentage/CGPA*", min_value=0.0, max_value=100.0, step=0.1, key="apply_grade10", help="Enter percentage. If CGPA, convert to percentage as per your board's rules.")

    with col4:
        grade_12_percentage = st.number_input("Grade 12 Percentage*", min_value=0.0, max_value=100.0, step=0.1, key="apply_grade12")

    st.write("Entrance Exam Details:")
    col5, col6 = st.columns(2)
    with col5:
         entrance_exam = st.selectbox("Entrance Exam Taken*", ["Select...", "JEE Main", "WBJEE", "CAT", "Other", "Not Applicable"], key="apply_exam")
    with col6:
        entrance_exam_rank = st.number_input("Entrance Exam Rank/Score", min_value=0, step=1, key="apply_rank", help="Enter your rank or score. Enter 0 if not applicable or exam not selected.")

    st.divider()

    # --- Document Upload ---
    st.subheader("📄 Document Upload")
    st.info(f"Allowed file types: {', '.join(ALLOWED_TYPES)}. Max size: {MAX_FILE_SIZE_MB}MB per file (Example Limit).")

    col_doc1, col_doc2 = st.columns(2)
    with col_doc1:
         uploaded_grade_10_marksheet = st.file_uploader(
             "Upload Class X Marksheet*",
             type=ALLOWED_TYPES,
             key="upload_grade10",
             help=f"Upload your Class 10 marksheet ({', '.join(ALLOWED_TYPES)})."
         )
    with col_doc2:
        uploaded_grade_12_marksheet = st.file_uploader(
            "Upload Class XII Marksheet*",
            type=ALLOWED_TYPES,
            key="upload_grade12",
            help=f"Upload your Class 12 marksheet ({', '.join(ALLOWED_TYPES)})."
        )

    uploaded_id_proof = st.file_uploader(
        "Upload ID Proof (Aadhaar, Passport, etc.)*",
        type=ALLOWED_TYPES,
        key="upload_id",
        help=f"Upload a government-issued ID proof ({', '.join(ALLOWED_TYPES)})."
    )

    # Optional: Allow uploading other relevant documents
    uploaded_other_docs = st.file_uploader(
        "Upload Other Supporting Documents (Optional)",
        type=ALLOWED_TYPES,
        accept_multiple_files=True, # Allow more than one optional doc
        key="upload_other",
        help=f"Upload any other relevant documents ({', '.join(ALLOWED_TYPES)})."
    )


    st.divider()

    # --- Parent/Guardian Information ---
    st.subheader("👨‍👩‍👧 Parent/Guardian Information")
    col7, col8 = st.columns(2)
    with col7:
        parent_name = st.text_input("Parent/Guardian Full Name*", key="apply_parent_name")
        parent_email = st.text_input("Parent/Guardian Email", key="apply_parent_email") # Optional
    with col8:
        parent_phone = st.text_input("Parent/Guardian Phone Number*", key="apply_parent_phone")

    st.divider()

    # --- Other Information ---
    st.subheader("💡 Other Information")
    interested_in_loan = st.checkbox("I am interested in applying for a student loan", key="apply_loan_interest")

    # --- Submission ---
    st.write("---")
    submitted = st.form_submit_button("Submit Application")

    if submitted:
        # --- File Upload Handling (Inside Submission Logic) ---
        # We check if the file uploader objects are not None

        grade10_marksheet_details = None
        if uploaded_grade_10_marksheet is not None:
            # **In a real app, save the file here:**
            # Eg: save_path = os.path.join("uploads", f"app_{st.session_state.next_app_id}_grade10_{uploaded_grade_10_marksheet.name}")
            # with open(save_path, "wb") as f:
            #     f.write(uploaded_grade_10_marksheet.getbuffer())
            grade10_marksheet_details = {"filename": uploaded_grade_10_marksheet.name, "size": uploaded_grade_10_marksheet.size}
            st.write(f"✔️ Class X Marksheet '{uploaded_grade_10_marksheet.name}' selected.") # User feedback
        else:
             st.write("⚠️ Class X Marksheet was not uploaded.") # User feedback


        grade12_marksheet_details = None
        if uploaded_grade_12_marksheet is not None:
            # **Save file here**
            grade12_marksheet_details = {"filename": uploaded_grade_12_marksheet.name, "size": uploaded_grade_12_marksheet.size}
            st.write(f"✔️ Class XII Marksheet '{uploaded_grade_12_marksheet.name}' selected.") # User feedback
        else:
             st.write("⚠️ Class XII Marksheet was not uploaded.") # User feedback

        id_proof_details = None
        if uploaded_id_proof is not None:
             # **Save file here**
             id_proof_details = {"filename": uploaded_id_proof.name, "size": uploaded_id_proof.size}
             st.write(f"✔️ ID Proof '{uploaded_id_proof.name}' selected.") # User feedback
        else:
             st.write("⚠️ ID Proof was not uploaded.") # User feedback

        other_docs_details = []
        if uploaded_other_docs: # Check if list is not empty
            for doc in uploaded_other_docs:
                 # **Save each file here**
                 other_docs_details.append({"filename": doc.name, "size": doc.size})
            st.write(f"✔️ {len(other_docs_details)} Other document(s) selected.") # User feedback
        else:
             st.write("ℹ️ No optional documents were uploaded.") # User feedback


        # --- Validation ---
        required_fields = {
            "Full Name": name,
            "Email Address": email,
            "Date of Birth": dob,
            "Gender": gender,
            "Permanent Address": address,
            "Course": course,
            "Grade 10 Percentage": grade_10_percentage,
            "Grade 12 Percentage": grade_12_percentage,
            "Entrance Exam Selection": entrance_exam,
            "Parent/Guardian Name": parent_name,
            "Parent/Guardian Phone": parent_phone,
        }
        optional_email_fields = {
             "Email Address": email,
             "Parent/Guardian Email": parent_email
        }
        # Check if required file uploaders have files
        required_uploads = {
            "Class X Marksheet": grade10_marksheet_details, # Check if details dict exists
            "Class XII Marksheet": grade12_marksheet_details,
            "ID Proof": id_proof_details,
        }

        errors = []
        for field_name, value in required_fields.items():
            if not value or (isinstance(value, (float, int)) and value <= 0) \
               or (field_name == "Gender" and value == "Select...") \
               or (field_name == "Entrance Exam Selection" and value == "Select..."):
                errors.append(f"'{field_name}' is required.")

        for field_name, value in optional_email_fields.items():
            if value and "@" not in value:
                 errors.append(f"Please enter a valid email address for '{field_name}'.")

        # Validate required uploads
        for field_name, details in required_uploads.items():
             if details is None: # Check if the details dict was created (meaning file was uploaded)
                 errors.append(f"'{field_name}' upload is required.")

        # Specific check for entrance exam rank if exam selected
        if entrance_exam not in ["Select...", "Not Applicable"] and entrance_exam_rank <= 0:
             errors.append("Please enter a valid Entrance Exam Rank/Score (> 0) if you selected an exam.")

        if errors:
            st.error("Please fix the following errors:\n\n" + "\n".join(f"- {error}" for error in errors))
        else:
            # --- Application Data Assembly ---
            app_id = st.session_state.next_app_id
            st.session_state.next_app_id += 1

            # Determine overall document status based on *required* uploads
            all_required_docs_uploaded = bool(grade10_marksheet_details and grade12_marksheet_details and id_proof_details)

            new_application = {
                "id": app_id,
                # Personal
                "name": name,
                "email": email,
                "dob": dob,
                "gender": gender,
                "address": address,
                # Academic
                "course": course,
                "grade_10_percentage": grade_10_percentage,
                "grade_12_percentage": grade_12_percentage,
                "entrance_exam": entrance_exam,
                "entrance_exam_rank": entrance_exam_rank if entrance_exam != "Not Applicable" else "N/A",
                # Document Meta-Data (NOT content)
                "grade10_marksheet_details": grade10_marksheet_details, # Dict with filename/size or None
                "grade12_marksheet_details": grade12_marksheet_details, # Dict with filename/size or None
                "id_proof_details": id_proof_details,                 # Dict with filename/size or None
                "other_docs_details": other_docs_details,             # List of dicts or empty list
                "docs_uploaded_status": all_required_docs_uploaded,   # Boolean based on required docs
                # Parent
                "parent_name": parent_name,
                "parent_phone": parent_phone,
                "parent_email": parent_email,
                # Other
                "loan_interest": interested_in_loan,
                # Status & Meta
                "status": "Application Submitted",
                "status_details": "Pending initial review (includes document verification).",
                "timestamp": pd.Timestamp.now(),
                "communication_history": [],
                "loan_status": "Not Requested" if not interested_in_loan else "Pending Request",
                "loan_amount_requested": 0 # Placeholder
            }

            st.session_state.applications.append(new_application)
            st.success(f"Application #{app_id} submitted successfully! Thank you, {name}. Your documents are being processed. You should receive an acknowledgment soon.")

            # Trigger initial communication
            with st.spinner("Processing submission and sending acknowledgment..."):
                # The agent now receives info about uploaded files (filenames, sizes)
                student_counsellor_agent(new_application)

            # Clear form fields by rerunning (Optional, use cautiously)
            # st.experimental_rerun()
            st.balloons()


st.write("---")
st.subheader("Submitted Applications (Current Session)")
if st.session_state.applications:
    # Select key columns for display, including doc status
    display_cols = ['id', 'name', 'email', 'course', 'grade_12_percentage', 'docs_uploaded_status', 'status', 'timestamp']
    apps_df = pd.DataFrame(st.session_state.applications)

    # Handle potential missing columns gracefully if structure changes later
    cols_to_show = [col for col in display_cols if col in apps_df.columns]

    # Prepare a display DF - Convert dicts/lists in columns to simple strings/indicators for display
    display_df = apps_df[cols_to_show].copy() # Work on a copy

    # Example: Simplify display of document details (optional, based on need)
    if 'grade10_marksheet_details' in apps_df.columns: # Check if column exists before trying to access it
       display_df['G10 Doc'] = apps_df['grade10_marksheet_details'].apply(lambda x: x['filename'] if x else 'Missing')
    if 'grade12_marksheet_details' in apps_df.columns:
        display_df['G12 Doc'] = apps_df['grade12_marksheet_details'].apply(lambda x: x['filename'] if x else 'Missing')
    if 'id_proof_details' in apps_df.columns:
        display_df['ID Doc'] = apps_df['id_proof_details'].apply(lambda x: x['filename'] if x else 'Missing')
    if 'other_docs_details' in apps_df.columns:
        display_df['Other Docs'] = apps_df['other_docs_details'].apply(lambda x: f"{len(x)} file(s)" if x else 'None')

    # Select final columns for st.dataframe (can include the simplified ones)
    final_display_cols = ['id', 'name', 'course', 'status', 'timestamp', 'G10 Doc', 'G12 Doc', 'ID Doc', 'Other Docs']
    # Filter final_display_cols to only include those actually present in display_df
    final_display_cols_present = [col for col in final_display_cols if col in display_df.columns]


    st.dataframe(display_df[final_display_cols_present])
else:
    st.info("No applications submitted in this session yet.")

# --- END OF FILE 1_📄_Apply_Now.py ---