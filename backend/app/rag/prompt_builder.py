"""
prompt_builder.py

Constructs the system prompt and the full prompt that is sent to the LLM.
Rules:
  - The LLM MUST only use the supplied context.
  - The LLM MUST cite sources.
  - The LLM MUST NOT hallucinate or invent facts.
"""

SYSTEM_PROMPT = """You are an Autonomous Knowledge Agent for an enterprise software team.

Your job is to answer questions about organisational decisions, technical choices,
feature development, and team activities — BASED STRICTLY on the Knowledge Context provided.

RULES YOU MUST FOLLOW:
1. ONLY use information explicitly present in the Knowledge Context below.
2. NEVER invent, guess, or extrapolate information not in the context.
3. If the answer is not in the context, respond EXACTLY with:
   "I couldn't find evidence for that in the available organisational knowledge."
4. ALWAYS cite the specific Feature, Platform, or Decision your answer is based on.
5. Structure your answer clearly with: Summary, Reasoning, Evidence, and Participants.
6. Keep your tone professional and concise.
"""


def build_prompt(question: str, context: str) -> str:
    """
    Construct the full prompt combining system instructions,
    retrieved context, and the user's question.
    """
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"=== KNOWLEDGE CONTEXT ===\n"
        f"{context}\n\n"
        f"=== USER QUESTION ===\n"
        f"{question}\n\n"
        f"=== YOUR ANSWER ===\n"
        f"Based only on the Knowledge Context above, provide a structured answer "
        f"with Summary, Reasoning, Evidence, and Participants."
    )


def build_debug_prompt(question: str, context: str) -> dict:
    """Return the prompt broken into parts for the debug endpoint."""
    return {
        "system_prompt": SYSTEM_PROMPT,
        "context": context,
        "question": question,
        "full_prompt": build_prompt(question, context),
    }
