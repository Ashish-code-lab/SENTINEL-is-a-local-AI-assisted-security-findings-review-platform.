from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from blue_agent import generate_defense
from judge_agent import judge_finding
from llama_engine import ModelUnavailableError
from red_agent import analyze_finding


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"


class ReviewRequest(BaseModel):
    finding: str = Field(min_length=20, max_length=20_000)


class ReviewResponse(BaseModel):
    review_id: str
    created_at: datetime
    red_report: str
    blue_report: str
    judge_report: str


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; object-src 'none'; "
            "base-uri 'self'; frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        return response


app = FastAPI(
    title="SENTINEL",
    description="Local-first analysis of supplied security scanner evidence.",
    version="1.0.0",
)
app.add_middleware(SecurityHeadersMiddleware)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/review", include_in_schema=False)
def review_workspace() -> FileResponse:
    return FileResponse(STATIC_DIR / "review.html")


@app.get("/tokens.css", include_in_schema=False)
def design_tokens() -> FileResponse:
    return FileResponse(ROOT / "tokens.css")


@app.get("/base.css", include_in_schema=False)
def design_base() -> FileResponse:
    return FileResponse(ROOT / "base.css")


@app.post("/api/reviews", response_model=ReviewResponse)
def create_review(payload: ReviewRequest) -> ReviewResponse:
    finding = payload.finding.strip()
    if len(finding) < 20:
        raise HTTPException(
            status_code=422,
            detail="Provide at least 20 non-whitespace characters of scanner evidence.",
        )

    try:
        red_report = analyze_finding(finding)
        blue_report = generate_defense(finding)
        judge_report = judge_finding(finding, red_report, blue_report)
    except ModelUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ReviewResponse(
        review_id=str(uuid4()),
        created_at=datetime.now(timezone.utc),
        red_report=red_report,
        blue_report=blue_report,
        judge_report=judge_report,
    )
