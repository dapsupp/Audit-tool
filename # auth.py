import streamlit_authenticator as stauth
import streamlit as st

def get_authenticator():
    """
    Handles authentication using Streamlit Authenticator.
    - Fixes outdated `.generate()` method issue.
    """
    names = ["Staff One", "Staff Two"]
    usernames = ["staff1", "staff2"]
    passwords = ["password1", "password2"]

    # Correct method for hashing passwords
    hashed_passwords = stauth.Hasher(passwords).generate_hashes()

    credentials = {
        "usernames": {
            "staff1": {"name": names[0], "password": hashed_passwords[0]},
            "staff2": {"name": names[1], "password": hashed_passwords[1]},
        }
    }

    authenticator = stauth.Authenticate(credentials, "cookie_name", "signature_key", cookie_expiry_days=30)
    return authenticator
