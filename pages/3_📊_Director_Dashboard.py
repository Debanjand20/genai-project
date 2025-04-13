import streamlit as st
import pandas as pd
from utils.helpers import initialize_session_state
from utils.agents import director_bot_agent


# Ensure state is initialized
initialize_session_state()

st.header("📊 Director Dashboard")
st.write("Ask questions about the admission process status.")

# Display Summary Stats
st.subheader("Quick Overview")
num_apps = len(st.session_state.get('applications', []))
apps_df = pd.DataFrame(st.session_state.get('applications', []))

col1, col2, col3 = st.columns(3)
col1.metric("Total Applications", num_apps)
if not apps_df.empty and 'status' in apps_df.columns:
    shortlisted_count = apps_df[apps_df['status'] == 'Shortlisted'].shape[0]
    confirmed_count = apps_df[apps_df['status'] == 'Admission Confirmed'].shape[0]
else:
    shortlisted_count = 0
    confirmed_count = 0
col2.metric("Shortlisted", shortlisted_count)
col3.metric("Admission Confirmed", confirmed_count)

col4, col5 = st.columns(2)
remaining_budget = st.session_state.get('available_loan_budget', 'N/A')
approved_loan_count = sum(1 for details in st.session_state.get('loan_requests', {}).values() if details['status'] == 'Loan Approved')
col4.metric("Remaining Loan Budget", f"${remaining_budget}")
col5.metric("Loans Approved", approved_loan_count)


# --- Conversational Bot ---
st.subheader("Ask the Admission Bot")
st.write("Examples: 'How many applications received?', 'Show status overview', 'What is the loan budget remaining?', 'What is the procedure after shortlisting?'")

query = st.text_input("Your question:", key="director_query")

if st.button("Ask Bot", key="director_ask"):
    if query:
        with st.spinner("Thinking..."):
            response = director_bot_agent(query)
            st.info("Bot Response:")
            st.markdown(response) # Use markdown for better formatting potentially
    else:
        st.warning("Please enter a question.")


st.subheader("Full Application List (Director's View)")
if not apps_df.empty:
    st.dataframe(apps_df[['id', 'name', 'course', 'status', 'status_details', 'loan_status', 'timestamp']])
else:
    st.info("No applications to display.")