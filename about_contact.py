import streamlit as st

st.set_page_config(page_title="About & Contact", page_icon="📬", layout="centered")

# --- About Us Section ---
st.title("📚 About Us")
st.markdown("""
Welcome to the Library Management System!  
Our mission is to make borrowing, tracking, and managing books simple and delightful.  
This system was built with ❤️ by Rehan to help users and admins manage library operations efficiently.
""")

st.divider()

# --- Contact Us Section ---
st.header("📬 Contact Us")

with st.form("contact_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Your Message")

    submitted = st.form_submit_button("Send Message")

    if submitted:
        if name and email and message:
            st.success("✅ Your message has been sent successfully!")
            # You can later add email integration or database logging here
        else:
            st.error("⚠️ Please fill out all fields before submitting.")