from agents import function_tool
from src.services.sheets_service import get_sheets_service


@function_tool
def add_sheet(
    spreadsheet_id: str,
    sheet_name: str,
) -> dict:
    """
    Adds a new sheet (tab) to an existing spreadsheet.
    Use this when the user wants to add a new sheet inside an existing file.
    Do NOT use create_spreadsheet for this — that creates a whole new file.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        sheet_name: Name for the new sheet (e.g. 'Summary', 'Q2 Data').
    """
    service = get_sheets_service()

    print(f"[TOOL] Adding new sheet {sheet_name}")

    result = (
        service.spreadsheets()
        .batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": sheet_name,
                            }
                        }
                    }
                ]
            },
        )
        .execute()
    )

    new_sheet = result["replies"][0]["addSheet"]["properties"]

    return {
        "sheet_name": new_sheet["title"],
        "sheet_id": new_sheet["sheetId"],
    }