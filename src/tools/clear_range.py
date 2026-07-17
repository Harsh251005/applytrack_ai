from agents import function_tool
from src.services.sheets_service import get_sheets_service


@function_tool
def clear_range(
    spreadsheet_id: str,
    sheet_name: str,
    start_cell: str,
    end_cell: str
) -> dict:
    """
    Clears all values in a range. Does not affect formatting.
    Call this before rewriting a range to avoid stale data.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        sheet_name: Exact sheet name (e.g. 'Sheet1'). Get this from schema.
        start_cell: Top-left cell of the range (e.g. 'A1').
        end_cell: Bottom-right cell of the range (e.g. 'D50').
    """
    service = get_sheets_service()

    print(f"Clearing range in {sheet_name} from {start_cell} to {end_cell}")

    range_name = f"{sheet_name}!{start_cell}:{end_cell}"

    result = (
        service.spreadsheets()
        .values()
        .clear(
            spreadsheetId=spreadsheet_id,
            range=range_name,
        )
        .execute()
    )

    return {
        "cleared_range": result.get("clearedRange"),
    }