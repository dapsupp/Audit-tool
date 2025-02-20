import streamlit as st
import auth
import pmax_audit_tool

authenticator = auth.get_authenticator()

def main():
    """
    Main entry point for the Streamlit app.
    """
    name, authentication_status, username = authenticator.login()

    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = authentication_status

    if "name" not in st.session_state:
        st.session_state["name"] = name

    if authentication_status:
        st.sidebar.success(f"Welcome, {st.session_state['name']}!")
        if st.sidebar.button("Logout"):
            authenticator.logout()
            st.session_state["authentication_status"] = False
            st.experimental_rerun()
        pmax_audit_tool.run_web_ui()
    elif authentication_status is False:
        st.sidebar.error("Invalid credentials.")
    else:
        st.sidebar.warning("Please log in.")

if __name__ == "__main__":
    main()
