import streamlit as st
import streamlit_authenticator as stauth

def get_authenticator():
    names = ["Staff One", "Staff Two"]
    usernames = ["staff1", "staff2"]
    passwords = ["password1", "password2"]

    # Correct hashing method
    hashed_passwords = stauth.Hasher(passwords).generate_hashes()

    credentials = {
        "usernames": {
            "staff1": {"name": names[0], "password": hashed_passwords[0]},
            "staff2": {"name": names[1], "password": hashed_passwords[1]},
        }
    }

    authenticator = stauth.Authenticate(credentials, "cookie_name", "signature_key", cookie_expiry_days=30)
    return authenticator
