from sales_service import get_sales_overview


def answer_sales_question(question: str) -> str:
    question_lower = question.lower()

    if (
        "summary" in question_lower
        or "overview" in question_lower
        or "total sales" in question_lower
        or "total revenue" in question_lower
        or "revenue" in question_lower
    ):
        data = get_sales_overview("2026-09")

        return (
            f"Sales overview for September 2026: "
            f"Revenue: {data.get('revenue')}, "
            f"Units Sold: {data.get('units_sold')}, "
            f"Orders: {data.get('orders')}, "
            f"Average Order Value: {data.get('average_order_value')}."
        )

    return (
        "I can currently answer sales overview and revenue questions. "
        "More sales intelligence capabilities will be added next."
    )