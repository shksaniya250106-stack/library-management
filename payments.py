import streamlit as st
from pathlib import Path
from db.connection import get_connection
import time
import random
from datetime import datetime, timedelta

# --- CSS LOADER ---
def load_css():
    css_path = Path(__file__).parent.parent / "styles" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# --- Authentication Check ---
if st.session_state.get("role") not in ["user", "admin"]:
    st.error("You need to be logged in to access this page.")
    st.page_link("main.py", label="Go to Login Page", icon="🏠")
    st.stop()

# --- DB Functions ---
def process_transaction(username, book_id, amount, transaction_type, due_date=None):
    """Logs payment and borrows/sells the book in the database."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Log the payment
        cur.execute(
            "INSERT INTO payments (username, book_id, amount, payment_type) VALUES (%s, %s, %s, %s)",
            (username, book_id, amount, transaction_type)
        )
        # 2. Mark book as unavailable (borrowed)
        cur.execute("UPDATE books SET available = 0 WHERE id = %s", (book_id,))
        # 3. If it's a rental, add it to the borrowed_books table with a due date
        if transaction_type == 'rent':
            cur.execute(
                "INSERT INTO borrowed_books (username, book_id, due_date) VALUES (%s, %s, %s)",
                (username, book_id, due_date)
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Database transaction failed: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# --- Main Page UI ---
load_css()
st.title("💳 Finalize Your Transaction")

# Check if a book was selected from the previous page
if 'book_to_purchase' not in st.session_state:
    st.warning("You have not selected a book. Please go back and choose a book to borrow or buy.")
    st.page_link("pages/available_books.py", label="Browse Books", icon="📖")
    st.stop()

book = st.session_state.book_to_purchase
st.header(f"You have selected: *{book['title']}*")

# --- Transaction Options ---
transaction_type = st.radio("Choose your transaction type:", ["Rent", "Buy"], horizontal=True)

# --- Mock OTP Payment Flow ---
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False

if transaction_type == "Rent":
    duration_options = {
        "7 Days": {"price": 1.99, "days": 7},
        "14 Days": {"price": 3.49, "days": 14},
        "30 Days": {"price": 5.99, "days": 30}
    }
    duration_choice = st.selectbox("Select rental duration:", options=list(duration_options.keys()))
    selected_option = duration_options[duration_choice]
    price = selected_option['price']
    st.subheader(f"Price: ${price:.2f}")
    if st.button("Proceed to Rent"):
        st.session_state.otp_sent = True
        st.session_state.transaction_details = {"type": "rent", "price": price, "days": selected_option['days']}

elif transaction_type == "Buy":
    price = 19.99
    st.subheader(f"Price: ${price:.2f}")
    if st.button("Proceed to Buy"):
        st.session_state.otp_sent = True
        st.session_state.transaction_details = {"type": "buy", "price": price}

st.divider()

# --- OTP Confirmation Step ---
if st.session_state.otp_sent:
    st.subheader("Confirm Your Identity")
    username_input = st.text_input("Enter your username to confirm", value=st.session_state.get("username", ""))

    if st.button("Send Mock OTP"):
        if username_input.lower() == st.session_state.get("username", "").lower():
            otp = random.randint(1000, 9999)
            st.session_state.mock_otp = otp
            st.success(f"OTP sent! (For testing, your OTP is: {otp})")
            time.sleep(5) # Keep the message on screen
            st.rerun()
        else:
            st.error("Username does not match the logged-in user.")

    if "mock_otp" in st.session_state:
        otp_input = st.text_input("Enter the 4-digit OTP you received")
        if st.button("Confirm Transaction"):
            if otp_input == str(st.session_state.mock_otp):
                details = st.session_state.transaction_details
                due_date = None
                if details['type'] == 'rent':
                    due_date = (datetime.now() + timedelta(days=details['days'])).date()

                if process_transaction(st.session_state.username, book['id'], details['price'], details['type'], due_date):
                    st.success(f"Transaction successful! You have {details['type']}ed '{book['title']}'.")
                    # Clean up session state
                    del st.session_state.book_to_purchase
                    del st.session_state.otp_sent
                    del st.session_state.mock_otp
                    del st.session_state.transaction_details
                    time.sleep(3)
                    st.switch_page("pages/available_books.py")
                else:
                    st.error("Your transaction could not be completed.")
            else:
                st.error("Invalid OTP.")
                