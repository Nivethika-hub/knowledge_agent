"""
llm_service.py

Manages the Groq API client as a singleton.
Exposes a simple call_llm() function that sends a prompt to
Llama 3.3 70B and returns the text response.
"""

import os
from groq import Groq
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

_GROQ_CLIENT: Optional[Groq] = None
_MODEL = "llama-3.3-70b-versatile"


def get_groq_client() -> Groq:
    """Return the singleton Groq client, creating it on first call."""
    global _GROQ_CLIENT
    if _GROQ_CLIENT is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )
        _GROQ_CLIENT = Groq(api_key=api_key)
    return _GROQ_CLIENT


def call_llm(prompt: str, temperature: float = 0.1, max_tokens: int = 1024) -> str:
    """
    Send a prompt to the Groq LLM and return the response text.

    Args:
        prompt      : The full prompt (system + context + question).
        temperature : Low value keeps answers factual and grounded.
        max_tokens  : Max response length.

    Returns:
        The LLM's text response as a string.
    """
    client = get_groq_client()
    response = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def call_llm_with_system(system: str, user_message: str,
                          temperature: float = 0.1, max_tokens: int = 1024) -> str:
    """
    Send separate system and user messages to the Groq LLM.
    Preferred form for LangChain-style structured prompting.
    """
    client = get_groq_client()
    response = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()
