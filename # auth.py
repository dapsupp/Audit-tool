import streamlit_authenticator as stauth
import os
from dotenv import load_dotenv

load_dotenv()

def get_authenticator():
    """
    Handles authentication using Streamlit Authenticator.
    - Uses hashed passwords stored securely to avoid rehashing on every run.
    """
    names = os.getenv("AUTH_NAMES")
    usernames = os.getenv("AUTH_USERNAMES")
    hashed_passwords = os.getenv("AUTH_HASHED_PASSWORDS")

    if not all([names, usernames, hashed_passwords]):
        raise ValueError("Missing required environment variables: AUTH_NAMES, AUTH_USERNAMES, AUTH_HASHED_PASSWORDS")

    names = names.split(",")
    usernames = usernames.split(",")
    hashed_passwords = hashed_passwords.split(";")

    if not (len(names) == len(usernames) == len(hashed_passwords)):
        raise ValueError("Mismatch in lengths of names, usernames, and hashed passwords.")

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
