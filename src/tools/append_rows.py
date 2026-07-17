from typing import List
from agents import function_tool
from src.tools.sheets_service import get_sheets_service


@function_tool
def append_rows(
    spreadsheet_id: str,
    sheet_name: str,
    values: list[List[str]]
) -> dict:
    """
    Appends rows to the end of existing data in a sheet.
    Use this instead of write_range when you don't know the next empty row.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        sheet_name: Exact sheet name (e.g. 'Sheet1'). Get this from schema.
        values: 2D list of rows to append. e.g. [["Harsh", 20], ["Priya", 22]]
    """
    service = get_sheets_service()

    print(f"[TOOL] Appending row to {sheet_name}")

    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",  # always adds new rows, never overwrites
            body={"values": values},
        )
        .execute()
    )

    updates = result.get("updates", {})

    return {
        "appended_range": updates.get("updatedRange"),
        "appended_rows": updates.get("updatedRows"),
        "appended_cells": updates.get("updatedCells"),
    }