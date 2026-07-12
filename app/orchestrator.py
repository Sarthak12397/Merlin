"""
Merlin GO — Orchestrator

Request -> Decision Agent -> Validator Agent -> Judge Agent -> Decision Record

Deliberately NOT a generic "Verification Orchestrator" abstraction yet (that's
the V2 full-architecture piece with 5 validators). This is the hardcoded
3-agent MVP loop from spec section 4 - prove the mechanics first.
"""

from app.models.schemas import DecisionRecord
from app.agents import decision_agent, validator_agent, judge_agent
from app.agents.client import MODEL_NAME, is_live
from app.store import audit_store


def run_cycle(request_text: str, idempotency_key: str = "") -> DecisionRecord:
    input_payload = {"request_text": request_text, "idempotency_key": idempotency_key}
    input_hash = DecisionRecord.compute_hash(input_payload)

    existing = audit_store.find_by_input_hash(input_hash)
    if existing is not None:
        return existing

    proposal = decision_agent.run(request_text)
    validation = validator_agent.run(request_text, proposal)
    verdict = judge_agent.run(request_text, proposal, validation)

    output_payload = {
        "proposal": proposal.model_dump(),
        "validation": validation.model_dump(),
        "verdict": verdict.model_dump(),
    }
    output_hash = DecisionRecord.compute_hash(output_payload)

    record = DecisionRecord(
        request_text=request_text,
        decision_agent_output=proposal,
        validator_output=validation,
        judge_output=verdict,
        input_hash=input_hash,
        output_hash=output_hash,
        model_version=MODEL_NAME if is_live() else "mock",
    )

    # PERSIST FIRST - fixes "judge succeeds but response is lost" (spec section 9).
    audit_store.persist(record)

    return record
