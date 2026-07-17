from googleapiclient.discovery import build

from src.authentication.google_auth import authenticate


def get_drive_service():
    creds = authenticate()

    return build(
        "drive",
        "v3",
        credentials=creds
    )