from agents import function_tool
from googleapiclient.discovery import build


@function_tool
def rename_spreadsheet(
    spreadsheet_id: str,
    new_name: str,
) -> str:
    """
    Rename a Google Spreadsheet.
    """

    from authentication.google_auth import authenticate

    creds = authenticate()

    drive_service = build(
        "drive",
        "v3",
        credentials=creds,
    )

    try:
        drive_service.files().update(
            fileId=spreadsheet_id,
            body={"name": new_name},
        ).execute()

        return (
            f'Spreadsheet renamed successfully to "{new_name}".'
        )

    except Exception as e:
        return f"Failed to rename spreadsheet: {e}"