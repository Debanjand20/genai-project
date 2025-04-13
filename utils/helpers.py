import streamlit as st
import pandas as pd
import time
import google.generativeai as genai

# -------------------------
# Gemini Model Initialization
# -------------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    st.error(f"Failed to initialize Gemini client. Check API key in secrets.toml: {e}")
    model = None

# -------------------------
# Session State Initialization
# -------------------------
def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    if 'applications' not in st.session_state:
        st.session_state.applications = []
    if 'next_app_id' not in st.session_state:
        st.session_state.next_app_id = 1
    if 'communication_log' not in st.session_state:
        st.session_state.communication_log = []
    if 'loan_requests' not in st.session_state:
        st.session_state.loan_requests = {}
    if 'available_loan_budget' not in st.session_state:
        st.session_state.available_loan_budget = 100000

# -------------------------
# Gemini Response Utilities
# -------------------------
def get_llm_response(prompt, context=""):
    """Gets a response from Gemini, optionally with context."""
    if not model:
        return "Error: Gemini model not initialized."

    full_prompt = f"{context}\n\nUser Query/Task: {prompt}\n\nAssistant Response:"
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error communicating with Gemini: {e}")
        return f"Error: Could not get response from Gemini. {e}"

def get_gemini_justification(application):
    """
    Uses Gemini to generate a justification for the loan request.
    """
    prompt = (
        f"Evaluate the student's loan request:\n"
        f"Name: {application['name']}\n"
        f"Requested Amount: {application.get('loan_amount_requested')}\n"
        f"Reason: {application.get('loan_reason')}\n"
        f"Course Status: {application.get('status')}\n"
        f"Course: {application.get('course', 'Not specified')}\n"
        f"Give a brief, professional justification on whether it seems valid."
    )
    return get_llm_response(prompt)

# -------------------------
# Communication Simulation
# -------------------------
def simulate_communication(app_id, student_email, message_type, details):
    """Simulates sending communication and logs it."""
    log_entry = {
        "timestamp": pd.Timestamp.now(),
        "app_id": app_id,
        "recipient": student_email,
        "type": message_type,
        "details": details
    }
    st.session_state.communication_log.append(log_entry)
    print(f"SIMULATING Email to {student_email}: {message_type} - {details}")
    time.sleep(0.5)

# -------------------------
# Fee Slip Generation
# -------------------------
def generate_fee_slip_content(application, fee_details, loan_details=None):
    content = f"--- Fee Slip ---\n"
    content += f"Application ID: {application['id']}\n"
    content += f"Student Name: {application['name']}\n"
    content += f"Course: {application.get('course', 'N/A')}\n\n"
    content += "Fee Breakdown:\n" + fee_details + "\n\n"

    total_fee = 10000  # Placeholder
    amount_due = total_fee

    if loan_details and loan_details.get('status') == "Loan Approved":
        approved_amount = loan_details.get('amount', 0)
        content += f"Loan Approved Amount: ${approved_amount}\n"
        amount_due -= approved_amount

    content += f"Amount Due: ${amount_due}\n"
    content += f"Payment Deadline: [Insert Deadline Here - e.g., 15 days from offer]\n"
    content += "--- End Fee Slip ---"
    return content
