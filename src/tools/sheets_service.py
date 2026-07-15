from googleapiclient.discovery import build

from authentication.google_auth import authenticate

def get_sheets_service():
    """
    Returns an authenticated Google Sheets service.
    """
    creds = authenticate()
    return build("sheets", "v4", credentials=creds)