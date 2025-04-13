import streamlit as st

# Title of the page
st.title("🎓 Admission Information Center")

# Define file paths
static_files = {
    "Admission Procedure": "data/admission_procedure.txt",
    "Eligibility Criteria": "data/eligibility_criteria.txt",
    "Fee Structure": "data/fee_structure.txt",
    "Loan Policy": "data/loan_policy.txt"
}

# Sidebar for selection
selected_section = st.sidebar.radio("Select a section:", list(static_files.keys()))

# Display content
file_path = static_files[selected_section]
try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    st.subheader(selected_section)
    st.text(content)
except FileNotFoundError:
    st.error(f"File '{file_path}' not found.")
