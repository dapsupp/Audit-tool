import streamlit_authenticator as stauth
import streamlit as st
import os

def get_authenticator():
    """
    Handles authentication using Streamlit Authenticator.
    - Secures credentials using environment variables instead of hardcoded passwords.
    """
    names = ["Staff One", "Staff Two"]
    usernames = ["staff1", "staff2"]
    
    # Retrieve passwords from environment variables
    passwords = [
        os.getenv("STAFF1_PASSWORD", "default_password"),
        os.getenv("STAFF2_PASSWORD", "default_password")
    ]

    # Hash passwords securely
    hashed_passwords = stauth.Hasher(passwords).generate()

    credentials = {
        "usernames": {
            usernames[0]: {"name": names[0], "password": hashed_passwords[0]},
            usernames[1]: {"name": names[1], "password": hashed_passwords[1]},
        }
    }

    authenticator = stauth.Authenticate(
        credentials, "cookie_name", "signature_key", cookie_expiry_days=30
    )
    return authenticator
