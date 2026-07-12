"""
Merlin GO v1 MVP — FastAPI entrypoint

Run with:
    uvicorn main:app --reload

Set ANTHROPIC_API_KEY in your environment first if you want real Claude calls.
Without it, agents run in deterministic mock mode (see agents.py).
"""

from fastapi import FastAPI
from pydantic import BaseModel
import store
from orchestrator import run_cycle

app = FastAPI(title="Merlin GO", version="1.0")


@app.on_event("startup")
def startup():
    store.init_db()


class DecisionRequest(BaseModel):
    request_text: str
    idempotency_key: str = ""


@app.post("/decisions")
def create_decision(req: DecisionRequest):
    record = run_cycle(req.request_text, req.idempotency_key)
    return record.model_dump()


@app.get("/decisions/{decision_id}")
def get_decision(decision_id: str):
    record = store.get_by_decision_id(decision_id)
    if record is None:
        return {"error": "not found"}
    return record.model_dump()


@app.get("/health")
def health():
    return {"status": "ok"}