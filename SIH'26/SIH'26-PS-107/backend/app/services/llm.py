# backend/app/services/llm.py
"""LLM abstraction layer.
Currently uses OpenAI's ChatCompletion API but the interface is intentionally
generic – it can be swapped for other providers later.
"""
import os
import logging
from typing import List, Dict, Any

import openai

logger = logging.getLogger(__name__)

# Environment variables – can be overridden per deployment.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("LLM_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set – LLM calls will fail unless a mock is used.")

openai.api_key = OPENAI_API_KEY

def _format_evidence(chunks: List[Dict[str, Any]]) -> str:
    """Create a textual representation of retrieved evidence for the LLM.
    Each entry is numbered and includes a short excerpt.
    """
    lines = []
    for idx, chunk in enumerate(chunks, start=1):
        excerpt = chunk.get("excerpt", "").replace("\n", " ")[:200]
        lines.append(f"[{idx}] {excerpt}")
    return "\n".join(lines)

def generate_answer(query: str, evidence_chunks: List[Dict[str, Any]]) -> str:
    """Call the LLM and obtain a grounded answer.
    The prompt explicitly instructs the model **not** to fabricate facts.
    """
    if not OPENAI_API_KEY:
        # Fallback mock – useful for tests without a real key.
        logger.info("OpenAI key missing – returning mock answer.")
        return "(Mock answer – LLM not configured)"

    if not evidence_chunks:
        return "I could not verify this from the available BIS sources."

    evidence_text = _format_evidence(evidence_chunks)
    system_prompt = (
        "You are an assistant that answers questions about Indian BIS standards. "
        "Only use the evidence provided below. Do not make up any information, "
        "including standard numbers, fees, or procedures. If the evidence does not "
        "contain enough information, respond exactly with: 'I could not verify this from the available BIS sources.'"
    )
    user_prompt = (
        f"Question: {query}\n\n"
        f"Evidence (numbered):\n{evidence_text}\n\n"
        "Provide a concise answer, citing the evidence numbers where appropriate."
    )
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.0,
            max_tokens=500,
        )
        answer = response.choices[0].message.content.strip()
        # Fallback if LLM hallucinations happen despite prompt
        if "i could not verify" in answer.lower() or "i couldn't verify" in answer.lower():
            return "I could not verify this from the available BIS sources."
            
        return answer
    except Exception as exc:  # pragma: no cover – defensive
        logger.error("LLM call failed: %s", exc)
        return "System temporarily unavailable: Could not generate a verified answer."
