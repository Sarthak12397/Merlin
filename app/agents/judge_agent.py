"""
Merlin GO — Judge Agent

Final decision maker. Does not invent facts, does not split the difference
into a comfortable middle answer — escalates when confidence is genuinely
insufficient rather than manufacturing certainty.
"""

from app.models.schemas import DecisionProposal, AgentOutput, JudgeVerdict
from app.agents.client import call_llm, is_live

SYSTEM_PROMPT = """You are the Judge Agent in Merlin GO — the final decision maker.
You do not invent new facts. Weigh the Decision Agent's proposal against the Validator's findings.
If evidence is insufficient or conflicting, escalate rather than guess.
Output JSON: {"final_decision": "approve|reject|escalate", "reason": str, "conflicts": [str]}

Example:
Proposal: {"proposal": "Approve refund", "confidence": 0.6}
Validator: {"decision": "uncertain", "confidence": 0.5, "risks": ["No photo evidence attached"], "missing_information": ["Photo of damaged item", "Account age"]}
Output:
{"final_decision": "escalate", "reason": "Decision Agent proposed approval based solely on an unverified customer claim; Validator found no supporting evidence and flagged missing account history. Confidence on both sides is too low to approve or reject outright.", "conflicts": []}

Notice this is NOT "Decision said approve, Validator said uncertain, so split the difference and approve with a note." Low confidence on both sides plus missing evidence means escalate — the Judge doesn't manufacture certainty that isn't there. If the two agents had made genuinely contradictory factual claims (not just different confidence), that goes in "conflicts" explicitly, named, not smoothed over."""


def run(request_text: str, proposal: DecisionProposal, validation: AgentOutput) -> JudgeVerdict:
    if is_live():
        user_prompt = (
            f"Request: {request_text}\n"
            f"Proposal: {proposal.model_dump_json()}\n"
            f"Validator finding: {validation.model_dump_json()}"
        )
        raw = call_llm(SYSTEM_PROMPT, user_prompt)
        return JudgeVerdict(**raw)
    # --- mock path ---
    return JudgeVerdict(
        final_decision="escalate",
        reason="Evidence insufficient",
        conflicts=[],
    )
