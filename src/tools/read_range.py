from langchain.tools import tool
from tools.sheets_service import get_sheets_service


@tool
def read_range(
    spreadsheet_id: str,
    range_name: str,
    render_formulas: bool = False
) -> list:
    """
    Reads values from a specified range.
    Set render_formulas=True to see raw formula strings.
    Default returns computed/displayed values (what the user sees).

    Example range: 'Sheet1!A1:C10'
    """
    service = get_sheets_service()

    print(f"[TOOL] Getting values from range {range_name}")

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueRenderOption="FORMULA" if render_formulas else "FORMATTED_VALUE"
        )
        .execute()
    )

    return result.get("values", [])