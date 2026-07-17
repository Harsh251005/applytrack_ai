from __future__ import annotations

import re
from typing import Any

from agents import function_tool
from googleapiclient.discovery import build

from src.authentication.google_auth import authenticate


def _color_to_hex(color: dict | None) -> str | None:
    """Convert Google Sheets RGB color dict to #RRGGBB."""
    if not color:
        return None

    r = round(color.get("red", 0) * 255)
    g = round(color.get("green", 0) * 255)
    b = round(color.get("blue", 0) * 255)

    return f"#{r:02X}{g:02X}{b:02X}"


def _normalize(value: Any) -> Any:
    """Normalize API enum strings."""
    if isinstance(value, str):
        return value.lower()
    return value


def _column_to_number(col: str) -> int:
    num = 0
    for c in col:
        num = num * 26 + (ord(c.upper()) - 64)
    return num


def _number_to_column(num: int) -> str:
    result = ""
    while num:
        num, rem = divmod(num - 1, 26)
        result = chr(65 + rem) + result
    return result


@function_tool
def read_formatting(
    spreadsheet_id: str,
    sheet_name: str,
    cell_range: str,
    include_defaults: bool = False,
) -> dict[str, Any]:
    """
    Read formatting for a range of cells.

    Returns only formatting information (no cell values).
    By default, only explicitly set formatting is returned to minimize tokens.
    """

    print("[TOOL] READ FORMATTING TOOL")

    creds = authenticate()
    service = build("sheets", "v4", credentials=creds)

    result = (
        service.spreadsheets()
        .get(
            spreadsheetId=spreadsheet_id,
            ranges=[f"{sheet_name}!{cell_range}"],
            includeGridData=True
        )
        .execute()
    )

    sheets = result.get("sheets", [])
    if not sheets:
        return {"formatting": {}}

    row_data = (
        sheets[0]
        .get("data", [{}])[0]
        .get("rowData", [])
    )

    match = re.match(r"([A-Z]+)(\d+)", cell_range.split(":")[0].upper())
    if not match:
        raise ValueError(f"Invalid A1 range: {cell_range}")

    start_col = _column_to_number(match.group(1))
    start_row = int(match.group(2))

    formatting = {}

    for r_idx, row in enumerate(row_data):

        for c_idx, cell in enumerate(row.get("values", [])):

            fmt = cell.get("userEnteredFormat")
            if not fmt:
                continue

            tf = fmt.get("textFormat", {})
            nf = fmt.get("numberFormat", {})

            cell_address = (
                f"{_number_to_column(start_col + c_idx)}"
                f"{start_row + r_idx}"
            )

            data = {
                "background_color": _color_to_hex(fmt.get("backgroundColor")),
                "text_color": _color_to_hex(tf.get("foregroundColor")),
                "bold": tf.get("bold"),
                "italic": tf.get("italic"),
                "underline": tf.get("underline"),
                "strikethrough": tf.get("strikethrough"),
                "font_family": tf.get("fontFamily"),
                "font_size": tf.get("fontSize"),
                "horizontal_alignment": _normalize(
                    fmt.get("horizontalAlignment")
                ),
                "vertical_alignment": _normalize(
                    fmt.get("verticalAlignment")
                ),
                "wrap_strategy": _normalize(
                    fmt.get("wrapStrategy")
                ),
                "number_format": (
                    {
                        "type": _normalize(nf.get("type")),
                        "pattern": nf.get("pattern"),
                    }
                    if nf
                    else None
                ),
            }

            if not include_defaults:
                data = {
                    key: value
                    for key, value in data.items()
                    if value not in (None, {}, False)
                }

            if data:
                formatting[cell_address] = data

    return {
        "sheet": sheet_name,
        "range": cell_range,
        "formatting": formatting,
    }
