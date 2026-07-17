from agents import function_tool

from src.services.sheets_service import get_sheets_service


@function_tool
def update_application_from_email(
    spreadsheet_id: str,
    sheet_name: str,
    row_number: int,
    company_name: str | None = None,
    job_title: str | None = None,
    status: str | None = None,
    application_date: str | None = None,
    interview_date: str | None = None,
    recruiter_name: str | None = None,
    recruiter_email: str | None = None,
    salary: str | None = None,
    location: str | None = None,
    application_link: str | None = None,
    notes: str | None = None,
) -> dict:
    """
    Updates one or more fields of an existing application.

    Only the fields provided (non-None) are updated.
    """

    service = get_sheets_service()

    updates = {
        "Company Name": company_name,
        "Job Title": job_title,
        "Status": status,
        "Application Date": application_date,
        "Interview Date": interview_date,
        "Recruiter Name": recruiter_name,
        "Recruiter Email": recruiter_email,
        "Salary": salary,
        "Location": location,
        "Application Link": application_link,
        "Notes": notes,
    }

    updates = {k: v for k, v in updates.items() if v is not None}

    if not updates:
        return {
            "updated": False,
            "message": "No fields to update."
        }

    headers = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!1:1",
        )
        .execute()
        .get("values", [[]])[0]
    )

    data = []

    for column_name, value in updates.items():

        if column_name not in headers:
            continue

        col = headers.index(column_name) + 1

        data.append(
            {
                "range": f"{sheet_name}!{column_to_letter(col)}{row_number}",
                "values": [[value]],
            }
        )

    if not data:
        return {
            "updated": False,
            "message": "None of the provided columns exist in the sheet."
        }

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": data,
        },
    ).execute()

    return {
        "updated": True,
        "updated_fields": list(updates.keys()),
    }


def column_to_letter(column: int) -> str:
    result = ""

    while column:
        column, remainder = divmod(column - 1, 26)
        result = chr(65 + remainder) + result

    return result