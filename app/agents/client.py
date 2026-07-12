"""
Merlin GO — shared LLM client setup.

Uses Google Gemini's free tier (Flash model) instead of a paid API.
If GEMINI_API_KEY is set, agents call Gemini for real.
If not, agents fall back to deterministic mock responses so the
LOOP MECHANICS can be proven without needing any key at all.

This matters: the MVP milestone (spec section 6) is about proving
normalization, disagreement representation, and persistence work —
not about proving an LLM can produce JSON. Don't conflate the two.

Get a free key (no credit card required) at https://aistudio.google.com
-> "Get API key" -> "Create API key in new project"
Then: export GEMINI_API_KEY=your-key-here
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gemini-flash-latest"
API_KEY = os.environ.get("GEMINI_API_KEY")

_client = None
if API_KEY:
    from google import genai
    _client = genai.Client(api_key=API_KEY)


def is_live() -> bool:
    return _client is not None


def call_llm(system_prompt: str, user_prompt: str) -> dict:
    """Calls Gemini, forces JSON-only output via response_mime_type, parses it.

    Retries transient server-side failures (503 overload, etc.) with backoff —
    this is spec section 9's 'LLM API failure / network retry' failure mode,
    made concrete instead of just named. After MAX_RETRIES, raises — the caller
    (orchestrator) is responsible for the retry-once-then-unavailable path for
    genuinely broken/malformed responses, which is a separate failure mode from
    this one (transient unavailability)."""
    import time
    from google.genai import types
    from google.genai.errors import ServerError

    MAX_RETRIES = 3
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            resp = _client.models.generate_content(
                model=MODEL_NAME,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )
            # Use raw_decode instead of loads: some Gemini responses include
            # trailing content after the JSON object even with response_mime_type
            # set to json. raw_decode parses just the first valid JSON value and
            # ignores anything after it, instead of crashing on "Extra data".
            decoder = json.JSONDecoder()
            parsed, _ = decoder.raw_decode(resp.text.strip())
            return parsed
        except ServerError as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(wait)
            continue

    # All retries exhausted — surface the failure, don't pretend it succeeded.
    raise last_error