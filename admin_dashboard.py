from pathlib import Path
import streamlit as st
from db.connection import get_connection
import hashlib
import cloudinary
import cloudinary.uploader

# --- CSS LOADER ---
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
    </style>
""", unsafe_allow_html=True)

# --- NEW: Cloudinary Configuration ---
# IMPORTANT: Replace these with your own Cloudinary credentials
try:
    cloudinary.config(
      cloud_name = st.secrets["cloudinary"]["cloud_name"],
      api_key = st.secrets["cloudinary"]["api_key"],
      api_secret = st.secrets["cloudinary"]["api_secret"],
      secure = True
    )
    CLOUDINARY_CONFIGURED = True
except (KeyError, Exception):
    CLOUDINARY_CONFIGURED = False

# --- Authentication Check ---
if st.session_state.get("role") != "admin":
    st.error("You need to be logged in as an Admin to access this page.")
    st.page_link("main.py", label="Go to Login Page", icon="🏠")
    st.stop()

# --- DB Helper Functions ---
def query_db(query, params=None, fetch="all", dictionary=False):
    """A generic database query function."""
    conn = get_connection()
    cur = conn.cursor(dictionary=dictionary)
    cur.execute(query, params or ())
    result = None
    if fetch == "one":
        result = cur.fetchone()
    elif fetch == "all":
        result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return result

# --- NEW: Image Upload Function ---
def upload_to_cloudinary(file_bytes, book_title):
    """Uploads an image to Cloudinary and returns the secure URL."""
    if not CLOUDINARY_CONFIGURED:
        st.error("Cloudinary is not configured. Please add your credentials to st.secrets.")
        return None
    try:
        upload_result = cloudinary.uploader.upload(
            file_bytes,
            public_id=f"library_posters/{book_title.replace(' ', '_')}",
            overwrite=True # Overwrite if a poster with the same title exists
        )
        return upload_result.get('secure_url')
    except Exception as e:
        st.error(f"Error uploading image: {e}")
        return None

# --- Stats, Book, and User Management Functions ---
def get_stats():
    """Fetches key statistics for the dashboard."""
    stats = {}
    stats['total_books'] = query_db("SELECT COUNT(*) FROM books", fetch="one")[0]
    stats['available_books'] = query_db("SELECT COUNT(*) FROM books WHERE available = TRUE", fetch="one")[0]
    stats['borrowed_books'] = query_db("SELECT COUNT(*) FROM borrowed_books", fetch="one")[0]
    stats['total_users'] = query_db("SELECT COUNT(*) FROM users", fetch="one")[0]
    return stats

def fetch_all_books(search=""):
    """Fetches all books, with an optional search filter."""
    like_term = f"%{search}%"
    return query_db("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s ORDER BY title", (like_term, like_term), dictionary=True)

def add_book(title, author, genre, poster_url):
    """Adds a new book to the database."""
    query_db("INSERT INTO books (title, author, genre, poster_url, available) VALUES (%s, %s, %s, %s, TRUE)", (title, author, genre, poster_url), fetch=None)

def update_book(book_id, title, author, genre, poster_url):
    """Updates a book's full details."""
    query_db("UPDATE books SET title = %s, author = %s, genre = %s, poster_url = %s WHERE id = %s",
             (title, author, genre, poster_url, book_id), fetch=None)

def delete_book(book_id):
    """Deletes a book from the database."""
    query_db("DELETE FROM books WHERE id = %s", (book_id,), fetch=None)

def fetch_all_users():
    """Fetches all users."""
    return query_db("SELECT id, username, role FROM users ORDER BY username", dictionary=True)

def add_user(username, password, role):
    """Adds a new user with a hashed password."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    query_db("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, hashed_password, role), fetch=None)

def delete_user(user_id):
    """Deletes a user."""
    query_db("DELETE FROM users WHERE id=%s", (user_id,), fetch=None)

# --- Transaction and Borrow History Functions ---
def fetch_transaction_history():
    """Fetches a detailed list of all payments."""
    return query_db(
        "SELECT p.id, p.username, b.title, p.amount, p.payment_type, p.payment_date FROM payments p JOIN books b ON p.book_id = b.id ORDER BY p.payment_date DESC",
        dictionary=True
    )

def fetch_borrowed_list():
    """Fetches currently rented books for the force return feature."""
    return query_db(
        "SELECT bb.id AS borrow_id, bb.username, b.id AS book_id, b.title, bb.borrow_date, bb.due_date FROM borrowed_books bb JOIN books b ON b.id = bb.book_id ORDER BY bb.due_date ASC",
        dictionary=True
    )

def force_return_book(borrow_id, book_id):
    """Admin function to force return a book."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM borrowed_books WHERE id = %s", (borrow_id,))
        cur.execute("UPDATE books SET available = TRUE WHERE id = %s", (book_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"DB error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# --- Main Admin Dashboard UI ---
load_css()
st.markdown('<div class="slide-in">', unsafe_allow_html=True)
st.markdown(f"<h1 class='bounce'>⚙️ Welcome, {st.session_state.get('username', 'Admin')}!</h1>", unsafe_allow_html=True)
st.write("This is the central dashboard for managing the library's books, users, and transactions.")
st.markdown('</div>', unsafe_allow_html=True)

# Stats Section
st.header("Library Stats")
stats = get_stats()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Books", stats['total_books'])
col2.metric("Available Books", stats['available_books'])
col3.metric("Rented Out", stats['borrowed_books'])
col4.metric("Total Users", stats['total_users'])
st.divider()

# Tabbed Interface
st.header("Management Sections")
book_tab, user_tab, transaction_tab = st.tabs(["📚 Books", "👥 Users", "💰 Transactions"])

# Book Management Tab
with book_tab:
    with st.expander("➕ Add a New Book", expanded=False):
        with st.form("add_book_form", clear_on_submit=True):
            title = st.text_input("Title")
            author = st.text_input("Author")
            genre = st.text_input("Genre")
            # --- UPDATED: File uploader for poster ---
            uploaded_file = st.file_uploader("Upload Book Poster", type=["png", "jpg", "jpeg"])
            
            if st.form_submit_button("Add Book"):
                poster_url = None
                if uploaded_file is not None:
                    # Read the file to bytes and upload it
                    file_bytes = uploaded_file.getvalue()
                    poster_url = upload_to_cloudinary(file_bytes, title)
                
                if poster_url or uploaded_file is None: # Proceed if upload was successful or no file was chosen
                    add_book(title, author, genre, poster_url)
                    st.success(f"Book '{title}' added!")
                    st.rerun()

    st.subheader("Existing Books")
    search_query = st.text_input("Search books by title or author", key="book_search")
    books = fetch_all_books(search_query)
    for book in books:
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])
            c1.image(book.get('poster_url', 'https://placehold.co/120x180/EEE/31343C?text=No+Image'), use_container_width=True)
            c2.subheader(book['title'])
            c2.write(f"by *{book['author']}*")
            with c2.expander("Edit / Delete"):
                new_title = st.text_input("Title", book['title'], key=f"title_{book['id']}")
                new_author = st.text_input("Author", book['author'], key=f"author_{book['id']}")
                new_genre = st.text_input("Genre", book['genre'], key=f"genre_{book['id']}")
                # --- UPDATED: File uploader for editing poster ---
                new_uploaded_file = st.file_uploader("Upload New Poster", type=["png", "jpg", "jpeg"], key=f"upload_{book['id']}")

                if st.button("Save Changes", key=f"save_{book['id']}"):
                    new_poster_url = book.get('poster_url', '') # Keep old URL by default
                    if new_uploaded_file is not None:
                        file_bytes = new_uploaded_file.getvalue()
                        new_poster_url = upload_to_cloudinary(file_bytes, new_title)
                    
                    if new_poster_url or new_uploaded_file is None:
                        update_book(book['id'], new_title, new_author, new_genre, new_poster_url)
                        st.success("Book updated!")
                        st.rerun()
                
                if st.button("🗑️ Delete", key=f"del_{book['id']}"):
                    delete_book(book['id'])
                    st.warning(f"Book '{book['title']}' deleted.")
                    st.rerun()

# User Management Tab
with user_tab:
    with st.expander("➕ Add a New User", expanded=False):
        with st.form("add_user_form", clear_on_submit=True):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["user", "admin"])
            if st.form_submit_button("Create User"):
                try:
                    add_user(username, password, role)
                    st.success(f"User '{username}' created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}. Username may already exist.")
    st.subheader("Existing Users")
    users = fetch_all_users()
    for user in users:
        cols = st.columns([3, 2, 1])
        cols[0].write(f"**Username:** {user['username']}")
        cols[1].write(f"**Role:** {user['role']}")
        if user['username'] != st.session_state.get("username"):
            if cols[2].button("🗑️ Delete", key=f"del_user_{user['id']}"):
                delete_user(user['id'])
                st.warning(f"User '{user['username']}' deleted.")
                st.rerun()

# Transaction History Tab
with transaction_tab:
    st.header("Transaction Management")
    st.subheader("Recent Payments (Rent & Buy)")
    transactions = fetch_transaction_history()
    if not transactions:
        st.info("No payment transactions have been recorded yet.")
    else:
        st.dataframe(transactions, use_container_width=True)

    st.subheader("Currently Rented Books (Force Return)")
    borrowed_list = fetch_borrowed_list()
    if not borrowed_list:
        st.info("No books are currently rented out.")
    else:
        for item in borrowed_list:
            cols = st.columns([2, 2, 2, 1])
            cols[0].write(f"**Book:** {item['title']}")
            cols[1].write(f"**Rented by:** {item['username']}")
            cols[2].write(f"**Due Date:** {item.get('due_date', 'N/A')}")
            if cols[3].button("Force Return", key=f"return_{item['borrow_id']}"):
                if force_return_book(item['borrow_id'], item['book_id']):
                    st.success(f"'{item['title']}' has been returned.")
                    st.rerun()