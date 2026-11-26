
from fastapi import FastAPI
from pydantic import BaseModel
from ai.llama_engine import ask_llama

app = FastAPI(
    title="SENTINEL AI Security Platform",
    description="Local AI-powered cybersecurity analysis",
    version="1.0"
)

class AnalysisRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return {
        "status": "online",
        "project": "SENTINEL",
        "ai_model": "llama3.2:3b"
    }

@app.post("/analyze")
def analyze(request: AnalysisRequest):
    result = ask_llama(request.prompt)

    return {
        "project": "SENTINEL",
        "analysis": result
    }
