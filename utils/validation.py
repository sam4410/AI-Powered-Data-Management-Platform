import re
import os
from pathlib import Path

def is_valid_sqlite_connection_string(conn_str: str) -> bool:
    """
    Validates whether the connection string:
    - Follows pattern: sqlite:///databases/<name>.db
    - Does not use placeholders like 'your_database_connection_string' or 'example.db'
    - Points to an existing .db file
    """

    # Basic pattern match
    pattern = r"^sqlite:///(databases|uploaded_dbs|[A-Za-z]:/.*)/[a-zA-Z0-9_\-]+\.db$"
    if not re.match(pattern, conn_str):
        return False

    # Strip prefix and get actual file path
    db_path = conn_str.replace("sqlite:///", "")
    db_file = Path(db_path)

    # Reject known invalid placeholders
    if db_file.name in {"example.db", "your_database_connection_string", "placeholder.db"}:
        return False

    # Check if file exists
    return db_file.is_file()
