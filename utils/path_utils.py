from pathlib import Path
from typing import Optional
from utils.validation import is_valid_sqlite_connection_string
import logging

logger = logging.getLogger(__name__)

def sanitize_connection_string(raw: str, strict: bool = True) -> Optional[str]:
    """
    Sanitize and validate a raw SQLite path or URI.

    Args:
        raw (str): File path or sqlite:/// URI
        strict (bool): If True, validate and return None on failure

    Returns:
        str or None: Valid sqlite:/// URI or None
    """
    try:
        if not raw:
            return None

        # If it's a URI but contains backslashes, force conversion
        if raw.startswith("sqlite:///"):
            raw_path = raw.replace("sqlite:///", "")
        else:
            raw_path = raw

        # Normalize slashes for cross-platform consistency
        raw_path = raw_path.replace("\\", "/")
        path_obj = Path(raw_path).resolve()

        if strict and not path_obj.exists():
            logger.warning(f"[sanitize_connection_string] ⚠️ File does not exist: {path_obj}")
            return None

        uri = f"sqlite:///{path_obj.as_posix()}"

        if strict and not is_valid_sqlite_connection_string(uri):
            logger.warning(f"[sanitize_connection_string] ❌ Invalid SQLite URI: {uri}")
            return None

        return uri

    except Exception as e:
        logger.error(f"[sanitize_connection_string] ❌ Exception occurred: {e}")
        return None
