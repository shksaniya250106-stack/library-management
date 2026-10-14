from pathlib import Path
import time
import streamlit as st

# Configure page (only keep in main.py ideally, but safe here if run standalone)
st.set_page_config(page_title="Library System", layout="wide")

# --- CSS Loader ---
def load_css():
    css_path = Path(__file__).parent / "styles" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    else:
        st.error(f"❌ CSS file not found at: {css_path}")

# --- Login Function ---
def user_login():
    # Animation styles
    st.markdown("""
        <style>
        .fade-out { animation: fadeOut 1.2s forwards; }
        @keyframes fadeOut { 0% {opacity: 1;} 100% {opacity: 0; transform: translateY(-15px);} }
        .slide-in { animation: slideIn 0.9s ease-out forwards; }
        @keyframes slideIn { 0% {opacity: 0; transform: translateX(50px);} 100% {opacity: 1; transform: translateX(0);} }
        .bounce { animation: bounceIn 1s ease forwards; }
        @keyframes bounceIn {
            0% {opacity: 0; transform: translateY(-20px);}
            50% {opacity: 1; transform: translateY(10px);}
            70% {transform: translateY(-5px);}
            100% {transform: translateY(0);}
        }
        .stagger-fade { opacity: 0; animation: fadeInStagger 0.6s ease forwards; }
        @keyframes fadeInStagger { to {opacity: 1; transform: translateY(0);} }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("👤 User Login")
    username = st.text_input("Username", key="user_login_username")
    password = st.text_input("Password", type="password", key="user_login_password")
    login_btn = st.button("Login", key="user_login_button")

    if login_btn:
        if username == "user1" and password == "pass123":
            st.session_state.logged_in = True
            st.session_state.role = "user"
            st.session_state.username = username

            st.success(f"Welcome, {username}!")
            st.markdown('<div class="fade-out"></div>', unsafe_allow_html=True)
            time.sleep(1.2)
            return True   # ✅ Success
        else:
            st.error("Invalid username or password.")
            return False   # ✅ Failure

    return False   # ✅ Default if no button pressed

# --- Dashboard with Slide, Bounce & Stagger ---
def user_dashboard():
    st.markdown('<div class="slide-in">', unsafe_allow_html=True)
    st.markdown(f"<h2 class='bounce'>📚 Library - User Dashboard</h2>", unsafe_allow_html=True)
    st.write(f"Welcome, {st.session_state.username} 👋")
    
    st.write("Borrow books, return them, and rate them — everything is saved to the database.")

    # Buttons stagger in
    btn_labels = ["Borrow Book", "Return Book", "Rate Book"]
    delay_ms = 200  # delay between buttons

    for idx, label in enumerate(btn_labels):
        st.markdown(
            f"<div class='stagger-fade' style='animation-delay:{idx * delay_ms}ms'>",
            unsafe_allow_html=True
        )
        st.button(label, key=f"user_dashboard_button_{idx}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)