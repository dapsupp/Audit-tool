import streamlit as st
import streamlit_authenticator as stauth

def get_authenticator():
    # Define user details (for demonstration only; store securely in production)
    names = ["Staff One", "Staff Two"]
    usernames = ["staff1", "staff2"]
    passwords = ["password1", "password2"]
    
    # Generate hashed passwords
    hashed_passwords = stauth.Hasher(passwords).generate()
    
    credentials = {
        "usernames": {
            "staff1": {"name": names[0], "password": hashed_passwords[0]},
            "staff2": {"name": names[1], "password": hashed_passwords[1]},
        }
    }
    
    # Create and return the authenticator object
    authenticator = stauth.Authenticate(credentials, "cookie_name", "signature_key")
    return authenticator
