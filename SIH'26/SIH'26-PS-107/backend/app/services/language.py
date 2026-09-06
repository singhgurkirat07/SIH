# backend/app/services/language.py
"""Utilities for language detection and translation.
We use the lightweight ``langdetect`` library for detecting the user language.
Translation is performed via OpenAI's ChatCompletion API – this keeps the
implementation simple and avoids external translation services. The API is
called with ``temperature=0`` to get deterministic output.
"""
import os
import logging
from typing import Literal

from langdetect import detect, LangDetectException
import openai

logger = logging.getLogger(__name__)

# Supported languages – extensible later.
SupportedLang = Literal["en", "hi"]

def detect_language(text: str) -> SupportedLang:
    """Return a language code (``en`` or ``hi``) for the given text.
    If detection fails or the language is not supported, default to English.
    """
    try:
        lang = detect(text)
    except LangDetectException:
        lang = "en"
    # Map langdetect codes to our supported set
    if lang.startswith("hi"):
        return "hi"
    return "en"

def translate_text(text: str, target: SupportedLang) -> str:
    """Translate *text* to *target* language.
    Uses OpenAI's ``gpt-4o-mini`` model with a clear system prompt. When the
    target language is the same as the source language we simply return the
    original text.
    """
    # Fast‑path for same language
    if target == detect_language(text):
        return text

    # Ensure we have an API key – otherwise return the original text (fallback).
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY missing – translation fallback to original text.")
        return text

    openai.api_key = api_key
    system_prompt = "You are a professional translator. Translate the given text to the requested language without adding, removing, or altering any technical terms. Keep the original meaning exactly."
    user_prompt = f"Translate the following text to {target.upper()}:\n\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.0,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:  # pragma: no cover – defensive
        logger.error("Translation failed: %s", exc)
        return text
}
