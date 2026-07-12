"""
Merlin GO v1 MVP — Agent Contract Schema
Every agent (Decision, Validator, Judge) must conform to this.
No free-form output. Section 5 of the locked spec.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime, timezone
import hashlib
import json
import uuid


class AgentOutput(BaseModel):
    """The strict schema every validator-style agent must return."""
    agent: str
    decision: Literal["approve", "reject", "uncertain", "unavailable"]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = []
    assumptions: list[str] = []
    risks: list[str] = []
    missing_information: list[str] = []
    counter_arguments: list[str] = []
    explanation: str = ""


class DecisionProposal(BaseModel):
    """Decision Agent's initial output — slightly different shape, it proposes rather than validates."""
    proposal: str
    assumptions: list[str] = []
    confidence: float = Field(ge=0.0, le=1.0)


class JudgeVerdict(BaseModel):
    """Judge Agent's final call. Section 8 of the spec."""
    final_decision: Literal["approve", "reject", "escalate"]
    reason: str
    conflicts: list[str] = []  # Section 9: contradictions must be named, not silently resolved


class DecisionRecord(BaseModel):
    """
    The persisted audit record. Section 6 + Section 9 (failure handling).
    This is written to the Audit Store BEFORE any response is returned to the caller —
    persistence is the source of truth, not the HTTP response.
    """
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_text: str
    decision_agent_output: DecisionProposal
    validator_output: AgentOutput
    judge_output: JudgeVerdict
    input_hash: str
    output_hash: str
    merlin_version: str = "1.0"
    prompt_version: str = "1.0"
    model_version: str = "unset"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @staticmethod
    def compute_hash(payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()