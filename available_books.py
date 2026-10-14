from pathlib import Path
import streamlit as st
from db.connection import get_connection

# --- Helper function to import components ---
def import_components():
    """Imports the book_card component, with error handling."""
    try:
        from components import book_card
        return book_card
    except ImportError:
        st.error("The `components.py` file could not be found. Please ensure it is in the root directory.")
        st.stop()
        return None

book_card = import_components()

# --- CSS LOADER ---
def load_css():
    """Loads the CSS file for styling the page."""
    css_path = Path(__file__).parent.parent / "styles" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS file not found.")

# --- Authentication Check ---
if st.session_state.get("role") not in ["user", "admin"]:
    st.error("You need to be logged in to access this page.")
    st.page_link("main.py", label="Go to Login Page", icon="🏠")
    st.stop()

# --- Database Functions ---
def fetch_genres():
    """Fetches all unique genres from the books table."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT genre FROM books ORDER BY genre")
        genres = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return ["All Genres"] + genres
    except Exception as e:
        st.error(f"Could not fetch genres: {e}")
        return ["All Genres"]

def fetch_all_books(search_term="", genre_filter="All Genres"):
    """Fetches all books, filtering by search term and genre."""
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        query = "SELECT * FROM books WHERE 1=1"
        params = []
        if search_term:
            query += " AND (title LIKE %s OR author LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        if genre_filter != "All Genres":
            query += " AND genre = %s"
            params.append(genre_filter)
        query += " ORDER BY title"
        cur.execute(query, tuple(params))
        books = cur.fetchall()
        cur.close()
        conn.close()
        return books
    except Exception as e:
        st.error(f"An error occurred while fetching books: {e}")
        return []

# --- Main Page UI ---
load_css()
st.title("📖 Available Books")
st.write("Browse our collection and select a book to rent or buy.")

# --- Search and Filter Controls ---
col1, col2 = st.columns([2, 1])
with col1:
    search_query = st.text_input("Search for a book by title or author", key="book_search")
with col2:
    available_genres = fetch_genres()
    selected_genre = st.selectbox("Filter by genre", options=available_genres, key="genre_filter")

# --- UPDATED: Borrow Callback now redirects to the payments page ---
def handle_borrow(book_id, book_title):
    """Saves the selected book's info to the session state and switches to the payment page."""
    st.session_state.book_to_purchase = {'id': book_id, 'title': book_title}
    st.switch_page("pages/payments.py")

# --- Display Books ---
all_books = fetch_all_books(search_query, selected_genre)
st.markdown("---")

if not all_books:
    st.info("No books found in the library matching your criteria.")
else:
    st.write(f"Found {len(all_books)} book(s).")
    num_columns = 4
    cols = st.columns(num_columns)
    for index, book in enumerate(all_books):
        with cols[index % num_columns]:
            # Each book card now uses the updated callback to go to the payments page
            book_card(book, borrow_callback=handle_borrow)