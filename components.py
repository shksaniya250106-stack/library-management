import streamlit as st
import time

def book_card(book, borrow_callback):
    """
    Renders a vertical book card with a large poster on top and details below,
    styled like a Netflix carousel.
    """
    st.markdown("""
        <style>
        .book-card {
            padding: 1rem;
            margin-bottom: 2rem;
            border-radius: 10px;
            background-color: #fdfdfd;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            text-align: center;
        }
        .book-poster {
            width: 100%;
            max-height: 300px;
            object-fit: cover;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .book-title {
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }
        .book-author {
            font-size: 16px;
            font-style: italic;
            color: #555;
            margin-bottom: 0.5rem;
        }
        .book-genre {
            font-size: 14px;
            color: #888;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="book-card">', unsafe_allow_html=True)

        # Poster image
        poster = book.get('poster_url')
        if poster:
            st.markdown(f'<img src="{poster}" class="book-poster">', unsafe_allow_html=True)
        else:
            st.markdown('<img src="https://placehold.co/300x400/EEE/31343C?text=No+Image" class="book-poster">', unsafe_allow_html=True)

        # Book details
        st.markdown(f"<div class='book-title'>{book.get('title', 'No Title')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='book-author'>by {book.get('author', 'Unknown Author')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='book-genre'>Genre: {book.get('genre', 'N/A')}</div>", unsafe_allow_html=True)

        # Borrow button or status
        is_available = bool(book.get('available', True))
        if is_available:
            if st.button("📖 Borrow Book", key=f"borrow_{book['id']}", use_container_width=True):
                borrow_callback(book['id'], book['title'])
        else:
            st.warning("Currently Borrowed", icon="⚠️")

        st.markdown('</div>', unsafe_allow_html=True)