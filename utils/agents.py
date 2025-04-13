# Note: These are *simulated* agents, represented by functions.
# In a real system, they'd be independent processes/services.
import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv


import random
from .helpers import get_llm_response, simulate_communication, generate_fee_slip_content
from .knowledge_base import query_knowledge_base, vector_store, raw_docs_content # Import the loaded KB

def document_checking_agent(application):
    """
    Simulates checking documents.
    In reality, this would involve file validation, possibly OCR.
    Here, we just check if required fields are non-empty (or simulated uploads exist).
    """
    st.write(f"🕵️ Document Agent checking application {application['id']}...")
    missing = []
    # Simulate checking based on form fields for simplicity
    if not application.get('docs_uploaded'):
        missing.append("Required Documents")
    if not application.get('grade_12_percentage'):
         missing.append("Grade 12 Percentage")

    if missing:
        status = "Documents Incomplete"
        details = f"Missing: {', '.join(missing)}"
        st.warning(f"App {application['id']}: {status} - {details}")
    else:
        status = "Documents Complete"
        details = "All required documents/info present."
        st.success(f"App {application['id']}: {status}")

    application['status'] = status
    application['status_details'] = details
    return status, details

def shortlisting_agent(application):
    """
    Simulates shortlisting based on simplified criteria from knowledge base.
    """
    st.write(f"📋 Shortlisting Agent evaluating application {application['id']}...")
    eligibility_info = ""
    if vector_store: # Use RAG
        context_docs = query_knowledge_base(vector_store, f"Eligibility criteria for {application.get('course', 'general courses')}", k=1)
        if context_docs:
            eligibility_info = context_docs[0].page_content # Get text from Langchain Document
    elif raw_docs_content: # Fallback to raw text
        eligibility_info = raw_docs_content.get('eligibility_criteria', '')

    if not eligibility_info:
        st.error("Could not retrieve eligibility criteria from Knowledge Base.")
        application['status'] = "Error - Criteria Missing"
        application['status_details'] = "Eligibility criteria not found."
        return application['status'], application['status_details']

    # Simple simulated check (replace with LLM reasoning or structured parsing)
    try:
        required_perc_str = eligibility_info.split("Minimum _PERCENTAGE_: ")[1].split('%')[0]
        required_percentage = float(required_perc_str)
        student_percentage = float(application.get('grade_12_percentage', 0))

        if student_percentage >= required_percentage:
            status = "Shortlisted"
            details = f"Eligible based on {required_percentage}% requirement."
            st.success(f"App {application['id']}: {status} - {details}")
        else:
            status = "Rejected - Eligibility"
            details = f"Does not meet {required_percentage}% requirement (has {student_percentage}%)."
            st.error(f"App {application['id']}: {status} - {details}")
    except (IndexError, ValueError, TypeError) as e:
        st.warning(f"Could not parse eligibility criteria automatically: {e}. Performing basic check.")
         # Fallback if parsing fails
        if application.get('grade_12_percentage', 0) > 60: # Generic fallback
            status = "Shortlisted"
            details = "Eligible based on fallback criteria."
            st.success(f"App {application['id']}: {status} - {details}")
        else:
            status = "Rejected - Eligibility"
            details = "Does not meet fallback criteria."
            st.error(f"App {application['id']}: {status} - {details}")


    application['status'] = status
    application['status_details'] = details
    return status, details

def student_counsellor_agent(application, message_type_override=None):
    """
    Simulates drafting and sending communication based on application status.
    Uses LLM with RAG for generating message content.
    """
    st.write(f"🗣️ Student Counsellor Agent preparing communication for application {application['id']}...")
    status = application['status']
    details = application['status_details']
    student_email = application['email']
    app_id = application['id']

    # Determine the type of communication needed
    if message_type_override:
        comm_type = message_type_override
    elif status == "Application Submitted":
        comm_type = "Application Acknowledgment"
    elif status == "Documents Incomplete":
        comm_type = "Incomplete Documents Notification"
    elif status == "Shortlisted":
        comm_type = "Provisional Offer Letter"
    elif status.startswith("Rejected"):
        comm_type = "Rejection Notification"
    elif status == "Admission Confirmed":
        comm_type = "Final Admission Letter & Fee Slip"
    elif status == "Loan Approved" or status == "Loan Rejected":
         comm_type = "Loan Status Update"
    else:
        comm_type = "Status Update" # Generic

    # Use RAG to get context for the message
    context = ""
    query = f"Draft an email for {comm_type}. Student Name: {application['name']}. Details: {details}."
    if vector_store:
        # Get relevant procedure/policy snippets
        context_docs = query_knowledge_base(vector_store, query, k=2)
        context = "\n---\nContext from Knowledge Base:\n" + "\n\n".join([doc.page_content for doc in context_docs]) + "\n---"

    # Generate message using LLM
    prompt = f"Generate a polite and professional email to the student ({student_email}) regarding their application (ID: {app_id}). The communication type is '{comm_type}'. Current status is '{status}' with details: '{details}'. Make sure to include next steps if applicable based on the context provided."
    message_body = get_llm_response(prompt, context=context)

    # Simulate sending
    simulate_communication(app_id, student_email, comm_type, message_body)
    st.info(f"App {app_id}: Communication '{comm_type}' simulated.")
    # Add message to application log?
    application.setdefault('communication_history', []).append(f"[{pd.Timestamp.now()}] {comm_type}: Message sent (simulated).")

    # If Admission Confirmed, also generate and "send" fee slip
    if status == "Admission Confirmed":
        fee_info = ""
        loan_details = st.session_state.loan_requests.get(app_id)
        if vector_store:
             fee_docs = query_knowledge_base(vector_store, f"Fee structure for {application.get('course', 'general')}", k=1)
             if fee_docs: fee_info = fee_docs[0].page_content
        elif raw_docs_content:
            fee_info = raw_docs_content.get('fee_structure', 'Fee details unavailable.')

        fee_slip_content = generate_fee_slip_content(application, fee_info, loan_details)
        simulate_communication(app_id, student_email, "Fee Slip", fee_slip_content)
        st.info(f"App {app_id}: Fee Slip generated and simulated sending.")
        application['communication_history'].append(f"[{pd.Timestamp.now()}] Fee Slip: Sent (simulated).")


def student_loan_agent(application):
    """
    Simulates processing a loan request based on policy and budget.
    """
    app_id = application['id']
    st.write(f"💰 Student Loan Agent processing request for application {app_id}...")

    if application['status'] != "Admission Confirmed": # Usually loan is processed after confirmation
         st.warning(f"App {app_id}: Loan processing deferred until admission is confirmed.")
         return "Deferred", "Admission not confirmed"


    loan_policy_info = ""
    if vector_store: # Use RAG
        context_docs = query_knowledge_base(vector_store, f"Student loan eligibility and policy", k=1)
        if context_docs:
            loan_policy_info = context_docs[0].page_content
    elif raw_docs_content: # Fallback
        loan_policy_info = raw_docs_content.get('loan_policy', '')

    if not loan_policy_info:
        st.error("Could not retrieve loan policy from Knowledge Base.")
        st.session_state.loan_requests[app_id] = {"status": "Error - Policy Missing", "details": "Loan policy not found."}
        return "Error", "Loan policy missing"

    # Simplified check (In reality, parse policy using LLM or rules)
    # Assume student meets basic criteria for demo
    eligible = True
    reason = "Eligible based on simplified check."
    max_loan_percentage = 0.80 # Default, ideally parse from policy_info
    requested_amount = application.get('loan_amount_requested', 5000) # Assume a requested amount

    # Placeholder for fee - fetch dynamically or use placeholder
    course_fee = 10000 # Example fee
    max_possible_loan = course_fee * max_loan_percentage

    approved_amount = 0
    if eligible:
        if requested_amount <= max_possible_loan:
            if st.session_state.available_loan_budget >= requested_amount:
                 status = "Loan Approved"
                 approved_amount = requested_amount
                 st.session_state.available_loan_budget -= approved_amount
                 details = f"Approved ${approved_amount}. Budget remaining: ${st.session_state.available_loan_budget}"
                 st.success(f"App {app_id}: {status} - {details}")
            else:
                status = "Loan Rejected"
                details = f"Insufficient university budget. Budget remaining: ${st.session_state.available_loan_budget}"
                st.error(f"App {app_id}: {status} - {details}")
        else:
            status = "Loan Rejected"
            details = f"Requested amount ${requested_amount} exceeds maximum allowed ${max_possible_loan} ({max_loan_percentage*100}% of fee)."
            st.error(f"App {app_id}: {status} - {details}")

    else:
        status = "Loan Rejected"
        details = reason # Use the reason from eligibility check
        st.error(f"App {app_id}: {status} - {details}")

    st.session_state.loan_requests[app_id] = {"status": status, "details": details, "amount": approved_amount}
    application['loan_status'] = status # Update application too if needed
    # Trigger communication agent
    student_counsellor_agent(application, message_type_override=status)

    return status, details


def director_bot_agent(query):
    """Handles queries from the director."""
    st.write(f"🤖 Director Bot processing query: '{query}'...")

    # Try to answer based on aggregated data first
    num_apps = len(st.session_state.get('applications', []))
    apps_df = pd.DataFrame(st.session_state.get('applications', []))
    response = None

    query_lower = query.lower()
    if "how many applications" in query_lower or "total applications" in query_lower:
        response = f"There are currently {num_apps} applications in the system."
    elif "status overview" in query_lower or "summary" in query_lower:
        if not apps_df.empty:
            status_counts = apps_df['status'].value_counts().to_dict()
            response = "Current application status overview:\n" + "\n".join([f"- {status}: {count}" for status, count in status_counts.items()])
        else:
            response = "No applications submitted yet."
    elif "shortlisted" in query_lower:
        count = 0
        if not apps_df.empty and 'status' in apps_df.columns:
            count = apps_df[apps_df['status'] == 'Shortlisted'].shape[0]
        response = f"There are {count} shortlisted applications."
    elif "loan budget" in query_lower:
        response = f"The remaining student loan budget is ${st.session_state.get('available_loan_budget', 'N/A')}."
    elif "approved loans" in query_lower:
        approved_count = sum(1 for details in st.session_state.get('loan_requests', {}).values() if details['status'] == 'Loan Approved')
        total_approved_amount = sum(details.get('amount',0) for details in st.session_state.get('loan_requests', {}).values() if details['status'] == 'Loan Approved')
        response = f"{approved_count} loans have been approved so far, totaling ${total_approved_amount}."

    # Fallback to Gemini LLM
    if response is None:
        st.write("Query not matched with predefined logic, using Gemini for LLM response...")

        # Set up Gemini
        load_dotenv()
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        try:
            model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
            prompt = f"""
            You are an assistant helping the director of a university understand the admission and loan process.
            Here's a user query: "{query}"

            If relevant, include information about application steps, shortlisting, loan eligibility, etc.
            Be clear and concise in your response.
            """
            gemini_response = model.generate_content(prompt)
            response = gemini_response.text
        except Exception as e:
            response = f"An error occurred while querying Gemini API: {e}"

    return response
