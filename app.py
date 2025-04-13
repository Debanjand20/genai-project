import streamlit as st
from utils.helpers import initialize_session_state

# Initialize session state MUST be the first Streamlit command
initialize_session_state()

st.set_page_config(
    page_title="Automated Admissions Demo",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Automated Student Admissions Demo")

st.write("""
Welcome to the simulated Automated Student Admissions system.
This application demonstrates how an agentic framework could potentially handle parts of the admission process.

**Use the sidebar to navigate between different views:**

*   **📄 Apply Now:** Simulate submitting a student application.
*   **🧑‍💼 Admission Officer View:** See the status of applications and manually trigger processing steps (simulating the orchestrator).
*   **📊 Director Dashboard:** Ask questions about the overall admission status.

**Disclaimer:** This is a **simulation** using Streamlit's session state.
- Data is **not persistent** and will be lost when you close the browser tab.
- Agents are represented by functions triggered manually or sequentially here.
- Requires an OpenAI API key configured in `.streamlit/secrets.toml`.
- Knowledge Base is loaded from simple `.txt` files in the `data/` directory.
""")

st.info("Please configure your OpenAI API key in `.streamlit/secrets.toml` before running.")

# You can add more introductory content or images here.