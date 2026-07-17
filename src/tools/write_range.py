from typing import List
from agents import function_tool
from src.tools.sheets_service import get_sheets_service


@function_tool
def write_range(
    spreadsheet_id: str,
    sheet_name: str,
    start_cell: str,
    values: list[List[str]]
) -> dict:
    """
    Writes a 2D list of values to a sheet starting from start_cell.
    Always call get_spreadsheet_schema first to confirm sheet name and structure.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        sheet_name: Exact sheet name (e.g. 'Sheet1'). Get this from schema.
        start_cell: Top-left cell to start writing from (e.g. 'A1', 'B3').
        values: 2D list of values. e.g. [["Name", "Age"], ["Harsh", 20]]
    """
    service = get_sheets_service()

    print(f"[TOOL] Writing values in {sheet_name}")

    range_name = f"{sheet_name}!{start_cell}"

    body = {"values": values}

    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",  # parses dates, formulas, etc.
            body=body,
        )
        .execute()
    )

    return {
        "updated_range": result.get("updatedRange"),
        "updated_rows": result.get("updatedRows"),
        "updated_columns": result.get("updatedColumns"),
        "updated_cells": result.get("updatedCells"),
    }
