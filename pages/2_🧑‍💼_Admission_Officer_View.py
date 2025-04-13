import streamlit as st
import pandas as pd
from utils.helpers import initialize_session_state
from utils.agents import (
    document_checking_agent,
    shortlisting_agent,
    student_counsellor_agent,
    student_loan_agent
)

# Ensure state is initialized
initialize_session_state()

st.header("🧑‍💼 Admission Officer Dashboard")
st.write("View applications and trigger processing steps (simulating orchestration).")

if not st.session_state.applications:
    st.info("No applications submitted yet.")
else:
    apps_df = pd.DataFrame(st.session_state.applications)

    st.subheader("Application Status Overview")
    st.dataframe(apps_df[['id', 'name', 'course', 'status', 'status_details', 'loan_status', 'timestamp']])

    st.subheader("Process Individual Applications")
    app_id_to_process = st.selectbox("Select Application ID to Process:", apps_df['id'])

    if app_id_to_process:
        # Find the application (convert back to dict for easier modification)
        app_index = apps_df[apps_df['id'] == app_id_to_process].index[0]
        # IMPORTANT: Work on a *copy* from session state list for modification
        # then update the original list element
        application = st.session_state.applications[app_index].copy()

        st.write(f"--- Processing Application #{application['id']} ({application['name']}) ---")
        st.write(f"Current Status: **{application['status']}**")

        col1, col2, col3, col4 = st.columns(4)

        # Button to trigger Document Check
        with col1:
            if st.button(f"Check Docs #{app_id_to_process}", key=f"check_{app_id_to_process}",
                         disabled=application['status'] not in ["Application Submitted", "Documents Incomplete"]):
                with st.spinner(f"Running Document Check Agent for {app_id_to_process}..."):
                    new_status, details = document_checking_agent(application)
                    st.session_state.applications[app_index] = application # Update the state list
                    # Trigger communication if incomplete
                    if new_status == "Documents Incomplete":
                         student_counsellor_agent(application)
                    st.rerun() # Refresh view

        # Button to trigger Shortlisting
        with col2:
            if st.button(f"Shortlist #{app_id_to_process}", key=f"shortlist_{app_id_to_process}",
                         disabled=application['status'] != "Documents Complete"):
                 with st.spinner(f"Running Shortlisting Agent for {app_id_to_process}..."):
                    new_status, details = shortlisting_agent(application)
                    st.session_state.applications[app_index] = application # Update state
                    # Trigger communication based on outcome
                    student_counsellor_agent(application)
                    st.rerun()

        # Button to Confirm Admission (Manual Step) & Trigger Final Comms
        with col3:
             if st.button(f"Confirm Admission #{app_id_to_process}", key=f"confirm_{app_id_to_process}",
                          disabled=application['status'] != "Shortlisted"):
                 application['status'] = "Admission Confirmed"
                 application['status_details'] = "Seat confirmed pending payment."
                 st.session_state.applications[app_index] = application
                 st.success(f"Admission confirmed for {app_id_to_process}.")
                 # Trigger final comms (letter + fee slip)
                 with st.spinner("Generating final letter & fee slip..."):
                    student_counsellor_agent(application)

                 # If loan was requested, trigger loan agent now
                 if application.get('loan_interest') and application['loan_status'] == 'Pending Request':
                      st.info("Triggering loan processing agent...")
                      with st.spinner("Processing Loan..."):
                           loan_status, loan_details = student_loan_agent(application)
                           # Loan agent handles its own communication now
                 st.rerun()


        # Button to Process Loan Request (if interest shown and admission confirmed)
        with col4:
             loan_processing_disabled = not (
                 application.get('loan_interest') and
                 application['status'] == "Admission Confirmed" and
                 application.get('loan_status') == 'Pending Request'
             )
             if st.button(f"Process Loan #{app_id_to_process}", key=f"loan_{app_id_to_process}",
                          disabled=loan_processing_disabled):
                 st.info("Triggering loan processing agent...")
                 with st.spinner("Processing Loan..."):
                    loan_status, loan_details = student_loan_agent(application)
                    # Loan agent handles its own communication
                 st.rerun()


        st.write("--- Communication Log ---")
        comm_log_df = pd.DataFrame(st.session_state.communication_log)
        if not comm_log_df.empty:
            st.dataframe(comm_log_df[comm_log_df['app_id'] == app_id_to_process].sort_values("timestamp", ascending=False))
        else:
            st.write("No communications logged yet.")