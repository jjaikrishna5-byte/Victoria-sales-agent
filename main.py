from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Victoria Sales Agent")


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    mode: str = "demo"


@app.get("/", include_in_schema=False)
@app.get("/index.html", include_in_schema=False)
def website():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/victoria-logo.png", include_in_schema=False)
def logo():
    return FileResponse(BASE_DIR / "victoria-logo.png")


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Victoria Sales Agent",
        "mode": "demo",
    }


def get_demo_answer(question: str) -> str:
    """Temporary sample responses until AI and database are connected."""
    question = question.lower()

    if "summary" in question:
        return (
            "September 2026 sample summary: revenue is $1,248,000, "
            "with 15,600 units sold and 1,240 orders. "
            "Kenya is the largest revenue market."
        )

    if "product" in question:
        return (
            "In the sample dataset, Samsung Galaxy A16 "
            "is the top-selling product with 5,400 units sold."
        )

    if "market" in question or "best" in question:
        return (
            "In the sample dataset, Kenya leads with $512,000 "
            "in revenue, followed by Tanzania at $374,400."
        )

    if "trend" in question or "revenue" in question:
        return (
            "Sample revenue increased from $820,000 in April "
            "to $1,248,000 in September. "
            "These are illustrative figures, not live sales records."
        )

    return (
        "The frontend is now connected to the Python backend. "
        "Try asking for a sales summary, top-selling products, "
        "market performance, or revenue trends. "
        "The AI model and database are not connected yet."
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return ChatResponse(answer=get_demo_answer(request.question))