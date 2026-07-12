"""
Merlin GO v1 MVP — Audit Store

Implements two non-negotiables from the locked spec (section 9):
1. Persist BEFORE responding — the DB write is the source of truth, not the HTTP response.
2. Idempotency — retrying with the same input must not create a second competing record.
"""

import sqlite3
import json
from pathlib import Path
from app.models.schemas import DecisionRecord

DB_PATH = Path(__file__).parent / "merlin_audit.db"


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decision_records (
            decision_id TEXT PRIMARY KEY,
            input_hash TEXT UNIQUE NOT NULL,
            output_hash TEXT NOT NULL,
            request_text TEXT NOT NULL,
            decision_agent_output TEXT NOT NULL,
            validator_output TEXT NOT NULL,
            judge_output TEXT NOT NULL,
            merlin_version TEXT NOT NULL,
            prompt_version TEXT NOT NULL,
            model_version TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def find_by_input_hash(input_hash: str) -> DecisionRecord | None:
    """Idempotency check. If this exact input already produced a decision, return it —
    do NOT re-run the agent chain. This is what stops a network retry from spawning
    a second competing Decision Record for the same request."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM decision_records WHERE input_hash = ?", (input_hash,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return DecisionRecord(
        decision_id=row["decision_id"],
        request_text=row["request_text"],
        decision_agent_output=json.loads(row["decision_agent_output"]),
        validator_output=json.loads(row["validator_output"]),
        judge_output=json.loads(row["judge_output"]),
        input_hash=row["input_hash"],
        output_hash=row["output_hash"],
        merlin_version=row["merlin_version"],
        prompt_version=row["prompt_version"],
        model_version=row["model_version"],
        timestamp=row["timestamp"],
    )


def persist(record: DecisionRecord) -> None:
    """Write the record. Called BEFORE the API layer returns anything to the caller.
    If the process dies or the network drops immediately after this call returns,
    the decision still exists and can be re-read by decision_id — it does not need
    to be re-judged."""
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO decision_records
        (decision_id, input_hash, output_hash, request_text, decision_agent_output,
         validator_output, judge_output, merlin_version, prompt_version, model_version, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.decision_id,
            record.input_hash,
            record.output_hash,
            record.request_text,
            record.decision_agent_output.model_dump_json(),
            record.validator_output.model_dump_json(),
            record.judge_output.model_dump_json(),
            record.merlin_version,
            record.prompt_version,
            record.model_version,
            record.timestamp,
        ),
    )
    conn.commit()
    conn.close()


def get_by_decision_id(decision_id: str) -> DecisionRecord | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM decision_records WHERE decision_id = ?", (decision_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return DecisionRecord(
        decision_id=row["decision_id"],
        request_text=row["request_text"],
        decision_agent_output=json.loads(row["decision_agent_output"]),
        validator_output=json.loads(row["validator_output"]),
        judge_output=json.loads(row["judge_output"]),
        input_hash=row["input_hash"],
        output_hash=row["output_hash"],
        merlin_version=row["merlin_version"],
        prompt_version=row["prompt_version"],
        model_version=row["model_version"],
        timestamp=row["timestamp"],
    )
