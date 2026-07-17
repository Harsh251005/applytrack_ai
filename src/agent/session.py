from agents.memory import SQLiteSession
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[2] / "data"

DATA_PATH.mkdir(parents=True, exist_ok=True)

MEMORY_DB_PATH = DATA_PATH / "tracker_memory.db"

session = SQLiteSession(
    session_id="tracker",
    db_path=MEMORY_DB_PATH
)
