from agents import function_tool

from src.services.sheets_service import get_sheets_service


@function_tool
def find_application_by_company(
    spreadsheet_id: str,
    sheet_name: str,
    header: str,
    company_name: str,
) -> dict:
    """
    Finds an application by company name.

    Args:
        spreadsheet_id: Spreadsheet ID.
        sheet_name: Sheet name.
        header: Header name for Company name.
        company_name: Company to search for.
    """

    print(f"Searching for {company_name} applications in {sheet_name}")

    service = get_sheets_service()

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
        )
        .execute()
    )

    values = result.get("values", [])

    if not values:
        return {"found": False}

    headers = values[0]

    try:
        company_col = headers.index(header)
    except ValueError:
        return {
            "found": False,
            "error": "Company Name column not found."
        }

    for row_index, row in enumerate(values[1:], start=2):
        if (
            len(row) > company_col
            and row[company_col].strip().lower() == company_name.strip().lower()
        ):
            return {
                "found": True,
                "row_number": row_index,
                "row_data": dict(zip(headers, row))
            }

    return {"found": False}
