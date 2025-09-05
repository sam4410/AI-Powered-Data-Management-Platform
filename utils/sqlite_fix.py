# SQLite3 fix for Streamlit Cloud
import sys

# Check if we're running on Streamlit Cloud or similar environment
try:
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
    print("Using pysqlite3 as sqlite3 replacement")
except ImportError:
    print("pysqlite3 not available, using system sqlite3")
    pass
