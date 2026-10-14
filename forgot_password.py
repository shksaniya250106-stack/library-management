import streamlit as st
from pathlib import Path
import random
import time
from db.connection import get_connection
import hashlib

# --- CSS Loader ---
def load_css():
    """Loads the CSS file for styling the page."""
    # --- FIX: Corrected the typo from _file_ to __file__ ---
    css_path = Path(__file__).parent.parent / "styles" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# --- Main Page UI ---
load_css()
st.title("🔑 Forgot Password")

# Use a specific session state key to avoid conflicts with other pages
if 'otp_sent_fp' not in st.session_state:
    st.session_state.otp_sent_fp = False

# Stage 1: Enter username to get OTP
if not st.session_state.otp_sent_fp:
    username = st.text_input("Enter your username to receive an OTP")

    if st.button("Send OTP"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username = %s", (username,))
        user_exists = cur.fetchone()
        cur.close()
        conn.close()

        if user_exists:
            otp = random.randint(100000, 999999)
            # Store OTP details in specific session state variables
            st.session_state.mock_otp_fp = otp
            st.session_state.otp_username_fp = username
            
            st.success(f"An OTP has been sent. (For testing, your OTP is: {otp})")
            
            # Pause to allow the user to see the OTP
            time.sleep(3)
            
            # Set the flag and rerun to move to the next stage
            st.session_state.otp_sent_fp = True
            st.rerun()
        else:
            st.error("Username not found. Please try again.")

# Stage 2: Enter OTP and new password
else:
    st.info(f"Enter the OTP sent for username: **{st.session_state.get('otp_username_fp')}**")
    otp_input = st.text_input("Enter OTP")
    new_pass = st.text_input("Enter new password", type="password")
    confirm_pass = st.text_input("Confirm new password", type="password")

    if st.button("Reset Password"):
        # Check if OTP is correct first
        if "mock_otp_fp" in st.session_state and otp_input == str(st.session_state.mock_otp_fp):
            # --- FIX: Added check to ensure passwords match ---
            if new_pass == confirm_pass:
                # Hash the new password before saving
                hashed_password = hashlib.sha256(new_pass.encode()).hexdigest()

                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET password = %s WHERE username = %s",
                    (hashed_password, st.session_state["otp_username_fp"])
                )
                conn.commit()
                cur.close()
                conn.close()

                st.success("Password has been reset successfully! Redirecting to login...")
                # Clean up all related session state keys
                for key in ["otp_sent_fp", "mock_otp_fp", "otp_username_fp"]:
                    if key in st.session_state:
                        del st.session_state[key]
                
                time.sleep(2)
                st.switch_page("main.py")
            else:
                st.error("The passwords you entered do not match.")
        else:
            st.error("The OTP you entered is invalid.")

st.divider()
st.page_link("main.py", label="Back to Login", icon="⬅️")