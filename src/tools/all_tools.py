from src.config.settings import settings
from src.tools.add_sheet import add_sheet
from src.tools.append_rows import append_rows
from src.tools.clear_range import clear_range
from src.tools.get_spreadsheet_schema import get_spreadsheet_schema
from src.tools.open_spreadsheet import open_spreadsheet
from src.tools.read_range import read_range
from src.tools.rename_spreadsheet import rename_spreadsheet
from src.tools.write_range import write_range
from src.tools.execute_code import make_execute_code_tool

execute_code = make_execute_code_tool(lambda: settings.SPREADSHEET_ID)

TOOLS = [
    add_sheet,
    append_rows,
    clear_range,
    get_spreadsheet_schema,
    open_spreadsheet,
    read_range,
    rename_spreadsheet,
    write_range,
    execute_code
]
