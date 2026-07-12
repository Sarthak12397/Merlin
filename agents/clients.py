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

MODEL_NAME = "gemini-2.5-flash"
API_KEY = os.environ.get("GEMINI_API_KEY")

_client = None
if API_KEY:
    from google import genai
    _client = genai.Client(api_key=API_KEY)


def is_live() -> bool:
    return _client is not None


def call_llm(system_prompt: str, user_prompt: str) -> dict:
    """Calls Gemini, forces JSON-only output via response_mime_type, parses it.
    Raises on malformed output — the caller (orchestrator) is responsible for
    the retry-once-then-unavailable path from spec section 9."""
    from google.genai import types

    resp = _client.models.generate_content(
        model=MODEL_NAME,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.3,
        ),
    )
    return json.loads(resp.text)