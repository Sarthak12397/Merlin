"""
Merlin GO — Decision Agent

Produces the initial proposal. Conservative by design — flags assumptions
explicitly rather than papering over uncertainty with confidence.
"""

from app.models.schemas import DecisionProposal
from app.agents.client import call_llm, is_live

SYSTEM_PROMPT = """You are the Decision Agent in Merlin GO, an AI decision assurance system.
Analyze the request and produce a proposal. Be conservative — flag assumptions explicitly.
Output JSON: {"proposal": str, "assumptions": [str], "confidence": float 0-1}

Example:
Request: "Should we approve this $500 refund for a customer who says the item arrived damaged?"
Output:
{"proposal": "Approve refund", "assumptions": ["Customer's damage claim is truthful", "No photo evidence has been reviewed"], "confidence": 0.6}

Notice the example does NOT inflate confidence just because refunds are routine — an unverified claim stays flagged as an assumption, and confidence reflects that gap."""


def run(request_text: str) -> DecisionProposal:
    if is_live():
        raw = call_llm(SYSTEM_PROMPT, request_text)
        return DecisionProposal(**raw)
    # --- mock path ---
    return DecisionProposal(
        proposal="Approve transaction",
        assumptions=["Customer identity is verified"],
        confidence=0.82,
    )