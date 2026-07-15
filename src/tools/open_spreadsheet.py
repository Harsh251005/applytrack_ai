import webbrowser
from langchain.tools import tool

@tool
def open_spreadsheet(spreadsheet_url: str) -> dict:
    """
    Opens a Google Spreadsheet in the user's default browser.
    Call this after creating a spreadsheet or when the user asks to open one.

    Args:
        spreadsheet_url: The full URL of the spreadsheet.
    """

    print(f"[TOOL] Opening {spreadsheet_url}")

    webbrowser.open(spreadsheet_url)

    return {"status": "opened", "url": spreadsheet_url}