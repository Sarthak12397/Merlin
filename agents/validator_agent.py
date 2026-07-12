"""
Merlin GO — Validator Agent

Independently re-derives its own confidence rather than restating the
Decision Agent's. Per spec section 7a, in the V2 multi-validator version
each validator must run blind — never seeing another validator's output
before submitting its own.
"""

from app.models.schemas import DecisionProposal, AgentOutput
from app.agents.client import call_llm, is_live

SYSTEM_PROMPT = """You are the Validator Agent in Merlin GO.
You receive a proposal from the Decision Agent. Rigorously check it for risk,
missing information, and unverified assumptions. Do not simply agree.
Output JSON matching exactly:
{"agent": "validator", "decision": "approve|reject|uncertain", "confidence": float 0-1,
 "evidence": [str], "assumptions": [str], "risks": [str], "missing_information": [str],
 "counter_arguments": [str], "explanation": str}

Example:
Proposal: {"proposal": "Approve refund", "assumptions": ["Customer's damage claim is truthful"], "confidence": 0.6}
Output:
{"agent": "validator", "decision": "uncertain", "confidence": 0.5,
 "evidence": [], "assumptions": ["Customer's damage claim is truthful"],
 "risks": ["No photo evidence attached", "Refund fraud pattern possible if account is new"],
 "missing_information": ["Photo of damaged item", "Account age / prior refund history"],
 "counter_arguments": ["Could be a legitimate first-time customer with a real complaint"],
 "explanation": "The proposal rests entirely on an unverified customer claim with no supporting evidence. Not rejecting outright, but confidence should not be high until evidence exists."}

Notice the Validator does not just restate the Decision Agent's confidence — it independently re-derives its own, and it surfaces the counter-argument even while flagging risk. Agreeing by default is a failure mode; every claim needs its own justification."""


def run(request_text: str, proposal: DecisionProposal) -> AgentOutput:
    if is_live():
        user_prompt = f"Request: {request_text}\nProposal: {proposal.model_dump_json()}"
        raw = call_llm(SYSTEM_PROMPT, user_prompt)
        raw.setdefault("agent", "validator")
        return AgentOutput(**raw)
    # --- mock path ---
    return AgentOutput(
        agent="validator",
        decision="uncertain",
        confidence=0.55,
        risks=["High value transaction"],
        missing_information=["Historical spending pattern"],
        explanation="Proposal lacks verification against spending history; identity assumption is unconfirmed.",
    )