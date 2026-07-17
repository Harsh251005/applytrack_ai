"""
execute_code tool — plug into your OpenAI Agents SDK spreadsheet agent.

Matches YOUR auth stack: raw googleapiclient services (sheets_service.py /
drive_service.py), not gspread. There's no formatting helper library for the
raw API, so this exposes small helper functions built on top of
spreadsheets().batchUpdate for the common jobs (coloring, conditional
formatting, merging, freezing, pivot tables, charts), plus the raw
`sheets_service` / `drive_service` objects for anything else.

No extra installs needed beyond what you already have
(google-api-python-client, google-auth-oauthlib).
"""

import io
import contextlib
import traceback

from pydantic import BaseModel, Field
from agents import function_tool

from src.services.sheets_service import get_sheets_service
from src.services.drive_service import get_drive_service


class ExecuteCodeInput(BaseModel):
    code: str = Field(
        description=(
            "Python code to run against the currently open spreadsheet.\n\n"
            "Available in scope:\n"
            "  sheets_service  -> authenticated Sheets API v4 service\n"
            "  drive_service   -> authenticated Drive API v3 service\n"
            "  spreadsheet_id  -> the currently open spreadsheet's ID (string)\n\n"
            "Helper functions:\n"
            "  get_sheet_id(title) -> numeric sheetId for a tab by name\n"
            "  rgb(r, g, b) -> color dict, r/g/b as 0-1 floats\n"
            "  batch_update(requests: list[dict]) -> runs spreadsheets().batchUpdate\n"
            "     with {'requests': requests}; returns the raw API response\n"
            "  format_range(sheet_id, start_row, end_row, start_col, end_col, "
            "background=None, bold=None, font_size=None, text_color=None) -> "
            "applies a repeatCell format over that 0-indexed, end-exclusive range\n"
            "  freeze_rows_cols(sheet_id, rows=0, cols=0)\n"
            "  merge_cells(sheet_id, start_row, end_row, start_col, end_col)\n"
            "  add_conditional_format(sheet_id, start_row, end_row, start_col, end_col, "
            "condition_type, condition_values, background) -> e.g. highlight cells "
            "where NUMBER_LESS than 0\n\n"
            "For anything not covered (pivot tables, charts, custom requests), build "
            "the raw request dict yourself and pass it to batch_update([...]) — see "
            "the Google Sheets API 'Request' reference for shapes like addPivotTable, "
            "addChart, updateDimensionProperties, etc.\n\n"
            "Use print() for anything you want reported back as output."
        )
    )


_BLOCKED_BUILTINS = {"open", "exec", "eval", "compile", "__import__", "input"}


def _safe_builtins():
    b = __builtins__
    if isinstance(b, dict):
        return {k: v for k, v in b.items() if k not in _BLOCKED_BUILTINS}
    return {k: getattr(b, k) for k in dir(b) if k not in _BLOCKED_BUILTINS}


def make_execute_code_tool(get_active_spreadsheet_id):
    """
    Factory — bind this to a getter that returns whichever spreadsheet_id is
    currently open (kept in sync with your open_spreadsheet tool's state).

    Example:
        current_spreadsheet_id = None  # set by your open_spreadsheet tool

        execute_code = make_execute_code_tool(lambda: current_spreadsheet_id)
    """

    sheets_service = get_sheets_service()
    drive_service = get_drive_service()

    @function_tool
    def execute_code(input: ExecuteCodeInput) -> str:
        """Execute Python code against the currently open spreadsheet to perform
        formatting, styling, conditional formatting, merging, freezing, pivot
        tables, charts, or dashboard-building tasks not covered by the other
        sheet tools."""

        print("Executing code")

        spreadsheet_id = get_active_spreadsheet_id()
        if not spreadsheet_id:
            return "Error: no spreadsheet is currently open. Call open_spreadsheet first."

        # ---- helpers built on the raw Sheets API ----

        def batch_update(requests: list) -> dict:
            return sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": requests}
            ).execute()

        def get_sheet_id(title: str) -> int:
            meta = sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            for sheet in meta["sheets"]:
                if sheet["properties"]["title"] == title:
                    return sheet["properties"]["sheetId"]
            raise ValueError(f"No sheet/tab named '{title}' found.")

        def rgb(r: float, g: float, b: float) -> dict:
            return {"red": r, "green": g, "blue": b}

        def format_range(sheet_id, start_row, end_row, start_col, end_col,
                          background=None, bold=None, font_size=None, text_color=None):
            cell_format = {}
            if background is not None:
                cell_format["backgroundColor"] = background
            text_format = {}
            if bold is not None:
                text_format["bold"] = bold
            if font_size is not None:
                text_format["fontSize"] = font_size
            if text_color is not None:
                text_format["foregroundColor"] = text_color
            if text_format:
                cell_format["textFormat"] = text_format

            fields = ",".join(f"userEnteredFormat.{k}" for k in cell_format) or "userEnteredFormat"

            return batch_update([{
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": start_row, "endRowIndex": end_row,
                        "startColumnIndex": start_col, "endColumnIndex": end_col,
                    },
                    "cell": {"userEnteredFormat": cell_format},
                    "fields": fields,
                }
            }])

        def freeze_rows_cols(sheet_id, rows=0, cols=0):
            return batch_update([{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {"frozenRowCount": rows, "frozenColumnCount": cols},
                    },
                    "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
                }
            }])

        def merge_cells(sheet_id, start_row, end_row, start_col, end_col):
            return batch_update([{
                "mergeCells": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": start_row, "endRowIndex": end_row,
                        "startColumnIndex": start_col, "endColumnIndex": end_col,
                    },
                    "mergeType": "MERGE_ALL",
                }
            }])

        def add_conditional_format(sheet_id, start_row, end_row, start_col, end_col,
                                    condition_type, condition_values, background):
            return batch_update([{
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": sheet_id,
                            "startRowIndex": start_row, "endRowIndex": end_row,
                            "startColumnIndex": start_col, "endColumnIndex": end_col,
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": condition_type,
                                "values": [{"userEnteredValue": v} for v in condition_values],
                            },
                            "format": {"backgroundColor": background},
                        },
                    },
                    "index": 0,
                }
            }])

        exec_globals = {
            "__builtins__": _safe_builtins(),
            "sheets_service": sheets_service,
            "drive_service": drive_service,
            "spreadsheet_id": spreadsheet_id,
            "batch_update": batch_update,
            "get_sheet_id": get_sheet_id,
            "rgb": rgb,
            "format_range": format_range,
            "freeze_rows_cols": freeze_rows_cols,
            "merge_cells": merge_cells,
            "add_conditional_format": add_conditional_format,
        }
        exec_locals = {}
        stdout_capture = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout_capture):
                exec(input.code, exec_globals, exec_locals)
            output = stdout_capture.getvalue().strip()
            return (
                f"Code executed successfully.\nOutput:\n{output}"
                if output else "Code executed successfully (no output)."
            )
        except Exception:
            err = traceback.format_exc()
            output = stdout_capture.getvalue().strip()
            msg = f"Error executing code:\n{err}"
            if output:
                msg += f"\nPartial output before error:\n{output}"
            return msg

    return execute_code