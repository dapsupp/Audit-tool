import streamlit_authenticator as stauth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_authenticator():
    """
    Handles authentication using Streamlit Authenticator.
    - Uses hashed passwords stored securely to avoid rehashing on every run.
    """
    names = os.getenv("AUTH_NAMES", "Staff One,Staff Two").split(",")
    usernames = os.getenv("AUTH_USERNAMES", "staff1,staff2").split(",")
    hashed_passwords = os.getenv("AUTH_HASHED_PASSWORDS", "").split(";")

    if len(usernames) != len(hashed_passwords):
        raise ValueError("Mismatch between usernames and stored password hashes.")

    credentials = {
        "usernames": {
            usernames[i]: {"name": names[i], "password": hashed_passwords[i]}
            for i in range(len(usernames))
        }
    }

    authenticator = stauth.Authenticate(
        credentials,
        cookie_name=os.getenv("AUTH_COOKIE_NAME", "cookie_name"),
        key=os.getenv("AUTH_SIGNATURE_KEY", "signature_key"),
        cookie_expiry_days=int(os.getenv("AUTH_COOKIE_EXPIRY_DAYS", "30"))
    )
    return authenticator
