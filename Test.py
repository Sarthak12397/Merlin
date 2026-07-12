"""
Proves the MVP milestone from spec section 6: one complete verification cycle,
plus proves idempotency (spec section 9): calling twice with the same input
does not create a second Decision Record.
"""

import store
from orchestrator import run_cycle

store.init_db()

print("=== RUN 1 (fresh request) ===")
record1 = run_cycle("Should this payment be approved?", idempotency_key="req-001")
print(f"Decision ID: {record1.decision_id}")
print(f"Proposal:    {record1.decision_agent_output.proposal} (confidence {record1.decision_agent_output.confidence})")
print(f"Validator:   {record1.validator_output.decision} (confidence {record1.validator_output.confidence})")
print(f"  risks: {record1.validator_output.risks}")
print(f"  missing: {record1.validator_output.missing_information}")
print(f"Judge:       {record1.judge_output.final_decision} — {record1.judge_output.reason}")
print(f"Model:       {record1.model_version}")

print("\n=== RUN 2 (same idempotency_key — should NOT re-run agents) ===")
record2 = run_cycle("Should this payment be approved?", idempotency_key="req-001")
print(f"Decision ID: {record2.decision_id}")
assert record1.decision_id == record2.decision_id, "FAIL: idempotency broken, got a new decision_id"
print("PASS: same decision_id returned, no duplicate record created.")

print("\n=== RUN 3 (different request — should be a new record) ===")
record3 = run_cycle("Should this refund be approved?", idempotency_key="req-002")
assert record3.decision_id != record1.decision_id, "FAIL: different requests collided"
print(f"Decision ID: {record3.decision_id} (new, as expected)")