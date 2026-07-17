from agents import function_tool
from src.services.sheets_service import get_sheets_service


@function_tool
def delete_sheet(
    spreadsheet_id: str,
    sheet_name: str,
) -> dict:
    """
    Deletes a sheet (tab) from an existing spreadsheet by name.
    Use this when the user wants to remove a sheet from a file.
    Never delete a sheet without confirming the sheet name from get_spreadsheet_schema first.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        sheet_name: Exact name of the sheet to delete. Get this from schema.
    """
    service = get_sheets_service()

    print(f"[TOOL] Deleting sheet {sheet_name}")

    # First fetch the sheetId — batchUpdate requires ID not name
    spreadsheet = (
        service.spreadsheets()
        .get(spreadsheetId=spreadsheet_id)
        .execute()
    )

    sheet_id = None
    for sheet in spreadsheet["sheets"]:
        if sheet["properties"]["title"] == sheet_name:
            sheet_id = sheet["properties"]["sheetId"]
            break

    if sheet_id is None:
        return {"error": f"Sheet '{sheet_name}' not found in spreadsheet."}

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {"deleteSheet": {"sheetId": sheet_id}}
            ]
        },
    ).execute()

    return {"deleted_sheet": sheet_name}