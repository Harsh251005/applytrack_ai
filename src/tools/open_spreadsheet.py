import webbrowser
from agents import function_tool

@function_tool
def open_spreadsheet(spreadsheet_name: str, spreadsheet_url: str) -> dict:
    """
    Opens a Google Spreadsheet in the user's default browser.
    Call this after creating a spreadsheet or when the user asks to open one.

    Args:
        spreadsheet_name: Name of the spreadsheet to open.
        spreadsheet_url: The full URL of the spreadsheet.
    """

    print(f"Opening {spreadsheet_name}")

    webbrowser.open(spreadsheet_url)

    return {"status": "opened", "url": spreadsheet_url}