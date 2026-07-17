from src.tools.sheets_service import get_sheets_service
from agents import function_tool


async def get_spreadsheet_schema_impl(spreadsheet_id: str) -> dict:
    """
    Returns the schema of a Google Spreadsheet — sheet names, headers,
    and row/column counts. Call this before writing to avoid hallucinations.
    """
    service = get_sheets_service()

    print(f"[TOOL] Getting schema for spreadsheet {spreadsheet_id}")

    # Get spreadsheet metadata (title + all sheet names)
    spreadsheet = (
        service.spreadsheets()
        .get(spreadsheetId=spreadsheet_id)
        .execute()
    )

    title = spreadsheet["properties"]["title"]
    sheets_info = []

    for sheet in spreadsheet["sheets"]:
        sheet_name = sheet["properties"]["title"]
        grid_props = sheet["properties"].get("gridProperties", {})

        # Read first row as headers + count non-empty rows
        result = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}"
            )
            .execute()
        )

        values = result.get("values", [])
        headers = values[0] if values else []
        row_count = len(values)
        col_count = max((len(row) for row in values), default=0)

        sheets_info.append({
            "sheet_name": sheet_name,
            "headers": headers,
            "row_count": row_count,
            "column_count": col_count,
        })

    return {
        "spreadsheet_title": title,
        "spreadsheet_id": spreadsheet_id,
        "number_of_sheets": len(sheets_info),
        "sheets": sheets_info,
    }

@function_tool
async def get_spreadsheet_schema(spreadsheet_id: str) -> dict:
    """Get the current worksheet/tab layout and column structure of the spreadsheet."""
    return await get_spreadsheet_schema_impl(spreadsheet_id)