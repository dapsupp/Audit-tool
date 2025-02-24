import streamlit as st
from auth import get_authenticator
import pmax_audit_tool

authenticator = get_authenticator()

def main():
    """
    Main entry point for the Streamlit app with authentication.
    """
    name, authentication_status, username = authenticator.login("Login", "main")

    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = authentication_status
    if "name" not in st.session_state:
        st.session_state["name"] = name

    if st.session_state["authentication_status"]:
        st.sidebar.success(f"Welcome, {st.session_state['name']}!")
        if st.sidebar.button("Logout"):
            authenticator.logout("Logout", "sidebar")
            st.session_state["authentication_status"] = False
            st.experimental_rerun()
        pmax_audit_tool.run_web_ui()
    elif st.session_state["authentication_status"] is False:
        st.sidebar.error("Invalid credentials.")
    else:
        st.sidebar.warning("Please log in.")

if __name__ == "__main__":
    main()
