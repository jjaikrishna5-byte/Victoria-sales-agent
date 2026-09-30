import sqlite3
from contextlib import contextmanager
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "victoria_demo.sqlite3"


@contextmanager
def get_connection():
    """Open the existing demo database in read-only mode."""
    if not DB_PATH.exists():
        raise RuntimeError(
            "Sample database not found. Run: python seed_data.py"
        )

    connection = sqlite3.connect(
        DB_PATH.as_uri() + "?mode=ro",
        uri=True,
    )
    connection.row_factory = sqlite3.Row

    try:
        yield connection
    finally:
        connection.close()


def initialize_database():
    """Create the local demo table if it does not exist."""
    connection = sqlite3.connect(DB_PATH)

    try:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    sale_id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL,
                    sale_date TEXT NOT NULL,
                    market TEXT NOT NULL,
                    product TEXT NOT NULL,
                    category TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    unit_price_cents INTEGER NOT NULL
                        CHECK (unit_price_cents >= 0),
                    currency TEXT NOT NULL DEFAULT 'USD'
                        CHECK (currency = 'USD')
                )
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_sales_date
                ON sales (sale_date)
            """)

    finally:
        connection.close()