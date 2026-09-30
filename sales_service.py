from datetime import date

from database import get_connection


def month_bounds(month: str):
    """Convert YYYY-MM into the start and end dates for that month."""
    try:
        start = date.fromisoformat(f"{month}-01")

        if start.strftime("%Y-%m") != month:
            raise ValueError

        if start.month == 12:
            end = date(start.year + 1, 1, 1)
        else:
            end = date(start.year, start.month + 1, 1)

        if start.month == 1:
            previous = date(start.year - 1, 12, 1)
        else:
            previous = date(start.year, start.month - 1, 1)

    except (ValueError, OverflowError):
        raise ValueError("Use a valid month in YYYY-MM format.")

    return start.isoformat(), end.isoformat(), previous.isoformat()


def get_sales_overview(month: str):
    start, end, previous = month_bounds(month)

    with get_connection() as connection:
        # Each order can contain multiple product lines.
        # COUNT(DISTINCT order_id) avoids counting an order twice.
        totals = connection.execute("""
            SELECT
                COUNT(*) AS sales_rows,
                COUNT(DISTINCT order_id) AS orders,
                COALESCE(SUM(quantity), 0) AS units,
                COALESCE(
                    SUM(quantity * unit_price_cents), 0
                ) AS revenue_cents
            FROM sales
            WHERE sale_date >= ? AND sale_date < ?
        """, (start, end)).fetchone()

        previous_totals = connection.execute("""
            SELECT
                COUNT(*) AS sales_rows,
                COALESCE(
                    SUM(quantity * unit_price_cents), 0
                ) AS revenue_cents
            FROM sales
            WHERE sale_date >= ? AND sale_date < ?
        """, (previous, start)).fetchone()

        market_rows = connection.execute("""
            SELECT
                market,
                SUM(quantity * unit_price_cents) AS revenue_cents,
                SUM(quantity) AS units
            FROM sales
            WHERE sale_date >= ? AND sale_date < ?
            GROUP BY market
            ORDER BY revenue_cents DESC, market ASC
        """, (start, end)).fetchall()

        product_rows = connection.execute("""
            SELECT
                product,
                category,
                SUM(quantity) AS units,
                SUM(quantity * unit_price_cents) AS revenue_cents
            FROM sales
            WHERE sale_date >= ? AND sale_date < ?
            GROUP BY product, category
            ORDER BY units DESC, product ASC
            LIMIT 10
        """, (start, end)).fetchall()

    revenue_cents = totals["revenue_cents"]
    previous_revenue_cents = previous_totals["revenue_cents"]
    orders = totals["orders"]
    units = totals["units"]

    # Growth is undefined when there is no previous revenue.
    # Missing current-month records also should not imply a sales decline.
    growth = None

    if totals["sales_rows"] > 0 and previous_revenue_cents > 0:
        growth = round(
            (
                (revenue_cents - previous_revenue_cents)
                / previous_revenue_cents
            ) * 100,
            2,
        )

    return {
        "mode": "sample_database",
        "month": month,
        "currency": "USD",
        "has_data": totals["sales_rows"] > 0,
        "summary": {
            "revenue": round(revenue_cents / 100, 2),
            "units_sold": units,
            "orders": orders,
            "average_order_value": (
                round(revenue_cents / orders / 100, 2)
                if orders > 0
                else None
            ),
            "revenue_growth_percent": growth,
            "previous_month_has_data": previous_totals["sales_rows"] > 0,
        },
        "markets": [
            {
                "market": row["market"],
                "revenue": round(row["revenue_cents"] / 100, 2),
                "units_sold": row["units"],
                "revenue_share_percent": (
                    round(row["revenue_cents"] / revenue_cents * 100, 2)
                    if revenue_cents > 0
                    else None
                ),
            }
            for row in market_rows
        ],
        "products": [
            {
                "product": row["product"],
                "category": row["category"],
                "units_sold": row["units"],
                "revenue": round(row["revenue_cents"] / 100, 2),
                "unit_share_percent": (
                    round(row["units"] / units * 100, 2)
                    if units > 0
                    else None
                ),
            }
            for row in product_rows
        ],
    }