from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from src.config.settings import settings

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def authenticate():
    ROOT_DIR = Path(__file__).resolve().parents[2]
    print(ROOT_DIR)

    CLIENT_SECRET_FILE = ROOT_DIR / settings.GOOGLE_CREDENTIALS_PATH
    TOKEN_FILE = ROOT_DIR / settings.GOOGLE_TOKEN_PATH

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_FILE),
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds
