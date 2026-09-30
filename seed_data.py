import sqlite3

from database import DB_PATH, get_connection, initialize_database


# Each row represents one product line within an order.
# Prices are stored in cents: 10000 cents = $100.00.
# All records are fictional, completed sales in USD.
SAMPLE_SALES = [
    # August
    (
        "S001", "ORD001", "2026-08-05", "Kenya",
        "Samsung Galaxy A16", "Smartphones", 10, 10000
    ),
    (
        "S002", "ORD001", "2026-08-05", "Kenya",
        "Nokia 105", "Feature phones", 5, 5000
    ),
    (
        "S003", "ORD002", "2026-08-12", "Tanzania",
        "Tecno Spark 30", "Smartphones", 8, 8000
    ),
    (
        "S004", "ORD003", "2026-08-18", "Uganda",
        "Infinix Hot 50", "Smartphones", 6, 7000
    ),
    (
        "S005", "ORD004", "2026-08-25", "Rwanda",
        "Nokia 105", "Feature phones", 4, 5000
    ),

    # September
    (
        "S006", "ORD005", "2026-09-03", "Kenya",
        "Samsung Galaxy A16", "Smartphones", 15, 10000
    ),
    (
        "S007", "ORD005", "2026-09-03", "Kenya",
        "Nokia 105", "Feature phones", 6, 5000
    ),
    (
        "S008", "ORD006", "2026-09-08", "Tanzania",
        "Tecno Spark 30", "Smartphones", 12, 8000
    ),
    (
        "S009", "ORD007", "2026-09-12", "Uganda",
        "Infinix Hot 50", "Smartphones", 9, 7000
    ),
    (
        "S010", "ORD008", "2026-09-15", "Rwanda",
        "Nokia 105", "Feature phones", 7, 5000
    ),
]


def seed_database():
    initialize_database()

    connection = sqlite3.connect(DB_PATH)

    try:
        with connection:
            connection.executemany("""
                INSERT INTO sales (
                    sale_id,
                    order_id,
                    sale_date,
                    market,
                    product,
                    category,
                    quantity,
                    unit_price_cents
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(sale_id) DO NOTHING
            """, SAMPLE_SALES)

    finally:
        connection.close()

    # Read back the records to verify the database.
    with get_connection() as connection:
        totals = connection.execute("""
            SELECT
                COUNT(*) AS sales_rows,
                COUNT(DISTINCT order_id) AS orders,
                COALESCE(SUM(quantity), 0) AS units,
                COALESCE(
                    SUM(quantity * unit_price_cents), 0
                ) AS revenue_cents
            FROM sales
        """).fetchone()

    print("Sample database ready.")
    print(f"Sales rows: {totals['sales_rows']}")
    print(f"Orders: {totals['orders']}")
    print(f"Units sold: {totals['units']}")
    print(f"Revenue: ${totals['revenue_cents'] / 100:,.2f}")


if __name__ == "__main__":
    seed_database()