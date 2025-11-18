# gmail_oauth.py
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Scope: readonly access to Gmail (minimal required)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

CREDENTIALS_FILE = "credentials.json"   # downloaded from Google Cloud Console
TOKEN_FILE = "token.json"

def get_gmail_service():
   
    creds = None

    # Load existing token if present
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception:
            creds = None

    # If no valid credentials, run local server flow to get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"{CREDENTIALS_FILE} not found. Place OAuth client JSON here."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # opens browser to authorize

        # Save the credentials for next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    # Build service
    service = build("gmail", "v1", credentials=creds)
    return service

if __name__ == "__main__":
    svc = get_gmail_service()
    print("Gmail service ready:", svc)
