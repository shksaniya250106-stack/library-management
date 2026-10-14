import streamlit as st
from pathlib import Path
from db.connection import get_connection

# --- CSS Loader ---
def load_css():
    """Loads the CSS file for styling the page."""
    css_path = Path(__file__).parent.parent / "styles" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# --- Animation Styles ---
st.markdown("""
    <style>
    .slide-in { animation: slideIn 0.9s ease-out forwards; }
    @keyframes slideIn { 0% {opacity: 0; transform: translateX(50px);} 100% {opacity: 1; transform: translateX(0);} }
    .bounce { animation: bounceIn 1s ease forwards; }
    @keyframes bounceIn {
        0% {opacity: 0; transform: translateY(-20px);}
        50% {opacity: 1; transform: translateY(10px);}
        70% {transform: translateY(-5px);}
        100% {transform: translateY(0);}
    }
    .stagger-fade { opacity: 0; animation: fadeInStagger 0.6s ease forwards; animation-fill-mode: both; }
    @keyframes fadeInStagger { to {opacity: 1; transform: translateY(0);} }
    </style>
""", unsafe_allow_html=True)

# --- Authentication Check ---
if st.session_state.get("role") not in ["user", "admin"]:
    st.error("You need to be logged in to access this page.")
    st.page_link("main.py", label="Go to Login Page", icon="🏠")
    st.stop()

# --- DB Function ---
def get_user_stats(username):
    """Fetches stats for the logged-in user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM borrowed_books WHERE username = %s", (username,))
    borrowed_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {'borrowed_count': borrowed_count}

# --- Main Page UI ---
load_css()

st.markdown('<div class="slide-in">', unsafe_allow_html=True)
st.markdown(f"<h1 class='bounce'>Welcome, {st.session_state.get('username')}!</h1>", unsafe_allow_html=True)
st.write("This is your personal library dashboard. What would you like to do today?")
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# --- User Stats ---
stats = get_user_stats(st.session_state.get("username"))
st.markdown(
    f"<div class='stagger-fade' style='animation-delay:200ms'>",
    unsafe_allow_html=True
)
st.metric("Books You're Currently Renting", stats['borrowed_count'])
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- Quick Actions ---
st.markdown(
    f"<div class='stagger-fade' style='animation-delay:400ms'>",
    unsafe_allow_html=True
)
st.header("Quick Actions")
col1, col2 = st.columns(2)

with col1:
    if st.button("📖 Browse & Rent Books", use_container_width=True):
        st.switch_page("pages/available_books.py")

with col2:
    if st.button("📕 View My Rented Books", use_container_width=True):
        st.switch_page("pages/borrowed_books.py")
st.markdown("</div>", unsafe_allow_html=True)