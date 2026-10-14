import streamlit as st
from pathlib import Path
from db.connection import get_connection

# --- CSS Loader ---
def load_css():
    """Loads the CSS file for styling the page."""
    css_path = Path(__file__).parent.parent / "styles" / "styles.css"
    if css_path.exists():
        # Added encoding='utf-8' to prevent potential UnicodeDecodeError
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS file not found.")

# --- Authentication Check ---
# Corrected to allow both 'user' and 'admin' to view the page.
if st.session_state.get("role") not in ["user", "admin"]:
    st.error("You need to be logged in to access this page.")
    st.page_link("main.py", label="Go to Login Page", icon="🏠")
    st.stop()

# --- DB Functions ---
def fetch_borrowed_books(username):
    """Fetches the books currently borrowed by a specific user."""
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        # Updated query to get book_id for the return logic
        query = """
            SELECT b.id AS book_id, b.title, b.author, b.poster_url, 
                   bb.borrow_date, bb.due_date, bb.id AS borrow_id
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.id
            WHERE bb.username = %s
            ORDER BY bb.due_date ASC
        """
        cur.execute(query, (username,))
        books = cur.fetchall()
        cur.close()
        conn.close()
        return books
    except Exception as e:
        st.error(f"Error fetching your borrowed books: {e}")
        return []

def return_book(borrow_id, book_id):
    """Handles the full logic for returning a book."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        # 1. Delete the record from the borrowed_books table
        cur.execute("DELETE FROM borrowed_books WHERE id = %s", (borrow_id,))
        # 2. Mark the book as available again in the books table
        cur.execute("UPDATE books SET available = TRUE WHERE id = %s", (book_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database error during return: {e}")
        return False

# --- Main Page UI ---
load_css()
st.title("📕 My Borrowed Books")
st.write("Here is a list of all the books you are currently renting.")

borrowed_books_list = fetch_borrowed_books(st.session_state.get("username"))

st.divider()

if not borrowed_books_list:
    st.info("You have not borrowed any books yet.")
    st.page_link("pages/available_books.py", label="Browse for Books", icon="📖")
else:
    for book in borrowed_books_list:
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.image(book.get('poster_url', "https://placehold.co/120x180/EEE/31343C?text=No+Image"))
            with col2:
                st.subheader(book.get('title'))
                st.write(f"by *{book.get('author')}*")
                st.write(f"Borrowed on: {book.get('borrow_date').strftime('%Y-%m-%d')}")
                st.write(f"**Due Date:** {book.get('due_date')}")
            with col3:
                # The button now calls the complete return_book function
                if st.button("Return Book", key=f"return_{book['borrow_id']}", use_container_width=True):
                    if return_book(book['borrow_id'], book['book_id']):
                        st.success(f"You have returned '{book['title']}'!")
                        st.rerun()