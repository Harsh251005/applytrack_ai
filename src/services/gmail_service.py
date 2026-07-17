from googleapiclient.discovery import build

from src.authentication.google_auth import authenticate


def get_gmail_service():
    creds = authenticate()
    return build("gmail", "v1", credentials=creds)