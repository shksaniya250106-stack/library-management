import streamlit as st
import hashlib
from db.connection import get_connection
import time


def admin_login():
    """
    Displays the admin login form and handles secure authentication against the database.
    """

    st.subheader("🛡️ Admin Login")

    with st.form("admin_login_form", clear_on_submit=False):
        username = st.text_input("Admin Username", key="admin_username")
        password = st.text_input("Password", type="password", key="admin_password")
        submitted = st.form_submit_button("Login")

        if submitted:
            # Clean inputs by removing leading/trailing whitespace
            clean_username = username.strip()
            clean_password = password.strip()

            if not clean_username or not clean_password:
                st.warning("Please enter both username and password.")
                return False

            try:
                conn = get_connection()
                cur = conn.cursor(dictionary=True)

                query = "SELECT password FROM users WHERE username = %s AND role = 'admin'"
                cur.execute(query, (clean_username,))

                user_record = cur.fetchone()

                cur.close()
                conn.close()

                if user_record:
                    hashed_password_from_db = user_record['password']

                    # Hash the password the user entered to compare
                    entered_password_hashed = hashlib.sha256(
                        clean_password.encode()
                    ).hexdigest()

                    if hashed_password_from_db == entered_password_hashed:
                        st.session_state.logged_in = True
                        st.session_state.role = "admin"
                        st.session_state.username = clean_username

                        st.success(f"Welcome, Admin {clean_username}!")

                        time.sleep(1.2)
                        st.rerun()

                        return True

                    else:
                        st.error(
                            "The username or password you entered is incorrect."
                        )
                        return False

                else:
                    st.error("No admin user found with that username.")
                    return False

            except Exception as e:
                st.error(f"An error occurred during login: {e}")
                return False

    return False