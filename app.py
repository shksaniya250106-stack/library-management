from pathlib import Path
import streamlit as st
from user_login import user_login
from admin_login import admin_login

# --- Page Config ---
st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed" # Collapse sidebar on login page
)

# --- CSS Loader ---
def load_css():
    """Loads the CSS file for styling the page."""
    css_path = Path(__file__).parent / "styles" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    else:
        st.error("CSS file not found. Please ensure styles/styles.css exists.")

# --- Initialize Session State ---
# This ensures that the variables are always available
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- Main App Logic (Gatekeeper) ---

# Load CSS on every page run
load_css()

# If user is not logged in, show the login interface
if not st.session_state.logged_in:
    st.title("📚 Library Management System")
    st.write("Please log in to continue.")

    # Let user choose role to login
    role_choice = st.radio("Login as:", ["User", "Admin"], key="role_selector", horizontal=True)

    if role_choice == "User":
        if user_login():
            # On successful login, rerun to navigate to the dashboard
            st.rerun()
    else:
        if admin_login():
            # On successful login, rerun to navigate to the dashboard
            st.rerun()
    
    # Link to forgot password page
    st.page_link("pages/5_🔒_Forgot_Password.py", label="Forgot your password?", icon="🔑")

# If user IS logged in, show a welcome message and let sidebar navigation work
else:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    if st.sidebar.button("Logout"):
        # Clear the session state
        for key in st.session_state.keys():
            del st.session_state[key]
        # Rerun to go back to the login screen
        st.rerun()

    st.title(f"Welcome to the Library, {st.session_state.username}!")
    st.write("Please use the sidebar to navigate to the different sections of the library.")
    st.info("If you don't see the sidebar, click the little '>' arrow in the top-left corner.")