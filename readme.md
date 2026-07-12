# Merlin GO
<p align="center">
  <img width="150" height="150" alt="image" src="https://github.com/user-attachments/assets/9f6c1f28-8d27-4125-a3a5-22e1bd83f1f9" />
</p>

## AI Decision Assurance Layer

Merlin GO is an AI Decision Assurance Layer designed to verify, challenge, explain, and audit AI-generated decisions before they affect real-world systems.

Merlin is not another AI model.

Merlin is the verification layer between AI decisions and production actions.

The goal is simple:

> If an AI makes a decision, Merlin should be able to explain why it was made, what evidence supported it, what risks existed, and how the decision can be replayed later.

---

# Vision

Modern AI systems can generate powerful decisions, but production systems require more than intelligence.

They require:

* Verification
* Explainability
* Evidence
* Accountability
* Auditability
* Deterministic workflows

Merlin provides a structured process for evaluating AI decisions before execution.

---

# Core Principles

## 1. Independent Verification

A decision should not be trusted because one model produced it.

Merlin uses independent validator agents to challenge decisions from different perspectives.

Examples:

* Logic validation
* Evidence validation
* Risk analysis
* Adversarial review
* Compliance review

---

## 2. Evidence-Based Decisions

Merlin does not rely on simple voting between agents.

It evaluates:

* Supporting evidence
* Missing evidence
* Contradictory evidence
* Assumptions
* Risks

The goal is reasoning over evidence, not counting opinions.

---

## 3. Replayable Decisions

Every Merlin decision should be reproducible.

A historical decision should answer:

* What was requested?
* What did each agent evaluate?
* Which model versions were used?
* Which prompts were used?
* What evidence existed?
* Why was the final decision reached?

If a decision cannot be replayed, it cannot be reliably audited.

---

# Architecture (Full Vision — see Project Status for what's actually built)

```
                 Client
                    |
                    v
             Decision Agent
                    |
                    v
        Verification Orchestrator
                    |
       +------------+-------------+
       |            |             |
       v            v             v
 Evidence      Logic          Risk
 Validator    Validator     Validator
       |            |             |
       +------------+-------------+
                    |
                    v
             Evidence Graph
                    |
                    v
           Conflict Detection
                    |
                    v
              Judge Agent
                    |
                    v
            Decision Engine
                    |
                    v
              Audit Store
```

---

# Merlin Workflow

```
Received
   |
   v
Proposed
   |
   v
Validating
   |
   v
Conflict Analysis
   |
   v
Judging
   |
   +--------+
   |        |
   v        v
Approved Rejected

   |
   v

Escalated
   |
   v
Archived
```

Every state transition is explicit and auditable.

---

# Agent Model

Every Merlin agent follows a strict contract.

Example:

```json
{
  "agent": "risk_validator",
  "decision": "uncertain",
  "confidence": 0.65,
  "evidence": [],
  "assumptions": [],
  "risks": [],
  "missing_information": [],
  "counter_arguments": [],
  "explanation": ""
}
```

Agents do not return uncontrolled free-form responses.

Structured outputs allow deterministic processing, comparison, and auditing.

---

# Components

## Decision Agent

Responsible for:

* Understanding the request
* Producing a proposal
* Listing assumptions
* Providing initial confidence

## Validator Agents

Each validator answers one specific question.

### Evidence Validator
Does available evidence support the proposal?

### Logic Validator
Is the reasoning internally consistent?

### Risk Validator
What could go wrong?

### Adversarial Validator
Can the proposal be proven incorrect?

### Compliance Validator
Does the proposal violate policy?

**Current MVP note:** only one general Validator is implemented so far — it folds risk/logic/missing-info checking into a single agent. The other four are named here as the target design; see Project Status.

## Judge Agent

The Judge does not invent new information.

It evaluates:

* Evidence quality
* Validator disagreements
* Confidence levels
* Risks

Output:

```
Approve
Reject
Escalate
```

---

# Decision Replay Engine (V2 — not yet built)

The Decision Replay Engine is Merlin's core audit capability.

A production incident should be answerable:

> Why did Merlin approve this decision three months ago?

The replay system reconstructs:

* Original request
* Agent prompts
* Model versions
* Validator outputs
* Evidence
* Judge reasoning
* Final decision

This follows event-sourcing principles:

> If you cannot replay it, you cannot reliably audit it.

The MVP already persists `input_hash`/`output_hash` on every decision — the seed of replay verification, even before the full replay engine exists.

---

# Audit Record

Every decision stores:

```
Request
Proposal
Validator Outputs
Evidence
Confidence Scores
Judge Reasoning
Final Decision

Merlin Version
Agent Version
Prompt Version
Model Version
Policy Version

Timestamp
Correlation ID
```

Nothing important is discarded.

---

# Failure Handling

Merlin treats failures as normal system states.

Handled scenarios:

* Validator timeout
* Agent failure
* LLM API failure / transient overload — retried with exponential backoff (implemented)
* Network retry
* Contradictory evidence — surfaced explicitly by the Judge, never silently resolved
* Missing information
* Judge failure
* Malformed / non-JSON agent output — tolerant JSON parsing via `raw_decode`, ignores trailing extra data (implemented)

Every failure must produce a known outcome. Unknown states are system failures.

---

# Security Requirements

Merlin follows production security principles:

* Immutable audit records
* Role-based access control
* Least privilege
* Input validation
* Structured logging
* Correlation IDs
* Secret management (`.env`, never committed — see `.gitignore`)
* Model and prompt version tracking

---

# Success Metrics

Merlin measures:

* Validation accuracy
* False approvals
* False rejections
* Escalation rate
* Evidence completeness
* Decision stability
* Latency
* Cost per verification

---

# Development Philosophy

Merlin is built around a simple idea:

AI systems should not only answer.

They should be able to defend their decisions.

The future of AI in critical systems requires:

* Verification before execution
* Evidence before confidence
* Auditability before trust

Merlin GO exists to make AI decisions accountable.

---

# Project Status

**Current Phase: Architecture Definition / MVP Development**

Implemented today:

```
Decision Agent
        |
        v
Validator Agent
        |
        v
Judge Agent
        |
        v
Audit Record (SQLite, persist-before-respond, idempotent)
```

Also implemented: retry-with-backoff on transient LLM failures, tolerant JSON parsing, input/output hashing on every record.

Future versions will introduce:

* Multiple validator agents (Evidence, Logic, Risk, Adversarial, Compliance run independently — never seeing each other's output before submitting, per the Validator Independence Rule)
* Evidence graph storage
* Decision replay engine
* Policy engines
* Human escalation workflows

---

# Project Structure

```
merlin_v2/
├── app/
│   ├── agents/
│   │   ├── client.py            # Gemini free-tier client (mock/live switch, retry logic)
│   │   ├── decision_agent.py
│   │   ├── validator_agent.py
│   │   └── judge_agent.py
│   ├── models/
│   │   └── schemas.py           # AgentOutput, DecisionProposal, JudgeVerdict, DecisionRecord
│   ├── store/
│   │   └── audit_store.py       # SQLite persistence, idempotency lookup
│   ├── api/
│   │   └── routes.py            # FastAPI app
│   └── orchestrator.py          # wires the 3 agents together
├── tests/
│   └── test_cycle.py            # proves the loop, no server needed
├── .gitignore
├── requirements.txt
└── README.md
```

---

# Running It

All commands run from the `merlin_v2/` root.

### 1. Set up a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a free Gemini API key (no credit card required)
Go to [aistudio.google.com](https://aistudio.google.com) → "Get API key" → "Create API key in new project".

### 4. Create a `.env` file in the `merlin_v2/` root
```
GEMINI_API_KEY=your-key-here
```
(No spaces around the `=`. Never commit this file — it's already in `.gitignore`.)

### 5. Prove the loop works
```bash
python -m tests.test_cycle
```

### 6. Or run it as an API
```bash
uvicorn app.api.routes:app --reload
```
```bash
curl -X POST http://127.0.0.1:8000/decisions \
  -H "Content-Type: application/json" \
  -d '{"request_text": "Should this payment be approved?", "idempotency_key": "req-001"}'
```

Without a `GEMINI_API_KEY` set, everything above still runs — agents fall back to deterministic mock responses so the loop mechanics can be verified without needing a key at all.