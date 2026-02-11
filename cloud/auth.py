import streamlit as st

def login():
    st.sidebar.subheader("🔐 Login (Demo Only)")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")

    if login_btn:
        if username == "admin" and password == "1234":
            st.session_state["authenticated"] = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials")
