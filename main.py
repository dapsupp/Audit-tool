import streamlit as st
import auth
import pmax_audit_tool

authenticator = auth.get_authenticator()
authenticator.login()

if st.session_state["authentication_status"]:
    st.sidebar.success(f"Welcome, {st.session_state['name']}!")
    pmax_audit_tool.run_web_ui()
else:
    st.sidebar.warning("Please log in to access the tool.")
