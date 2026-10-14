# main.py - Your Main Application Entrypoint
from pathlib import Path
import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS Loader ---
def load_css():
    """Loads CSS and Google Fonts for the 'Vintage Library' theme."""
    css_path = Path(__file__).parent / "styles" / "styles.css"
    if css_path.exists():
        st.markdown("""
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,400..700&display=swap" rel="stylesheet">
        """, unsafe_allow_html=True)
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# --- Imports for Login Components ---
try:
    from user_login import user_login
    from admin_login import admin_login
except ImportError:
    st.error("Fatal Error: `user_login.py` and `admin_login.py` must be in the same directory.")
    st.stop()

# --- Initialize Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- Main Application Logic ---
load_css()

# --- If the user IS logged in ---
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    st.sidebar.page_link("pages/about_contact.py", label="📬 About / Contact Us")
    
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.success(f"Welcome back, {st.session_state.username}!")
    st.info("Please select a page from the sidebar to continue.")

# --- If the user is NOT logged in ---
else:
    st.title("📚 Library Management System")
    st.write("Please log in to continue.")

    role_choice = st.radio("Login as:", ["User", "Admin"], horizontal=True)

    if role_choice == "User":
        if user_login():
            st.session_state.logged_in = True
            st.session_state.username = "User"
            st.switch_page("pages/user_dashboard.py")
    else:
        if admin_login():
            st.session_state.logged_in = True
            st.session_state.username = "Admin"
            st.switch_page("pages/admin_dashboard.py")

    st.divider()

    if st.button("Forgot your password?", use_container_width=True):
        st.switch_page("pages/forgot_password.py")

    st.markdown(
        """
        <div style="text-align: center; margin-top: 2rem; font-style: italic; color: #6B4F4B;">
            "I have always imagined that Paradise will be a kind of library."
            <br>
            - Jorge Luis Borges
        </div>
        """,
        unsafe_allow_html=True
    )