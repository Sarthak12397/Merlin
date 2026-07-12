"""
Merlin GO — FastAPI entrypoint

Run from the merlin_v2/ root with:
    uvicorn app.api.routes:app --reload

Set ANTHROPIC_API_KEY in your environment first if you want real Claude calls.
Without it, agents run in deterministic mock mode.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from app.store import audit_store
from app.orchestrator import run_cycle

app = FastAPI(title="Merlin GO", version="1.0")


@app.on_event("startup")
def startup():
    audit_store.init_db()


class DecisionRequest(BaseModel):
    request_text: str
    idempotency_key: str = ""


@app.post("/decisions")
def create_decision(req: DecisionRequest):
    record = run_cycle(req.request_text, req.idempotency_key)
    return record.model_dump()


@app.get("/decisions/{decision_id}")
def get_decision(decision_id: str):
    record = audit_store.get_by_decision_id(decision_id)
    if record is None:
        return {"error": "not found"}
    return record.model_dump()


@app.get("/health")
def health():
    return {"status": "ok"}
