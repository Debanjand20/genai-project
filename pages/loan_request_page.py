import streamlit as st
from utils.helpers import initialize_session_state, get_gemini_justification
from utils.agents import student_loan_agent

# Initialize app state
initialize_session_state()

def loan_request_page(applications):
    st.title("💰 Student Loan Request Portal")

    eligible_apps = [app for app in applications if app["status"] == "Admission Confirmed"]

    if not eligible_apps:
        st.info("No applications are eligible for loan requests. (Only 'Admission Confirmed' allowed.)")
        return

    selected_app_label = st.selectbox(
        "Select your confirmed application",
        [f"{app['id']} - {app['name']}" for app in eligible_apps]
    )

    app_id = selected_app_label.split(" - ")[0]
    application = next((app for app in eligible_apps if str(app["id"]) == app_id), None)

    if not application:
        st.error("Selected application not found.")
        return

    st.markdown(f"### Application Details")
    st.markdown(f"**Application ID**: {application['id']}")
    st.markdown(f"**Name**: {application['name']}")
    st.markdown(f"**Email**: {application['email']}")
    st.markdown(f"**Status**: {application['status']}")

    with st.form("loan_form"):
        st.subheader("📄 Submit Loan Request")

        uploaded_docs = st.file_uploader("Upload supporting documents", type=["pdf", "jpg", "png"])
        amount_requested = st.number_input("Enter Loan Amount Requested", min_value=1000, max_value=50000, value=5000, step=500)
        reason = st.text_area("Reason for Loan Request", height=150)

        submitted = st.form_submit_button("Submit")

    if submitted:
        if not uploaded_docs or not reason:
            st.warning("Please upload your document and provide a reason.")
            return

        application['loan_amount_requested'] = amount_requested
        application['loan_reason'] = reason

        st.markdown("#### 🤖 Gemini Justification")
        justification = get_gemini_justification(application)
        st.info(justification)

        status, details = student_loan_agent(application)
        st.success(f"Loan Status: {status}")
        st.markdown(f"**Details**: {details}")

# Call the page function if this is the main file
if __name__ == "__main__":
    loan_request_page(st.session_state.applications)
