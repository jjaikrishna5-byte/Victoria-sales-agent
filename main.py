from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field

from agent import answer_sales_question
from sales_service import get_sales_overview


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Victoria Sales Agent")


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    mode: str


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
        "mode": "database-backed",
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer = answer_sales_question(request.question)

        return ChatResponse(
            answer=answer,
            mode="database",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to process the sales question.",
        ) from error


@app.get("/api/sales/overview")
def sales_overview(month: str = "2026-09"):
    try:
        return get_sales_overview(month)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve sales overview.",
        ) from error