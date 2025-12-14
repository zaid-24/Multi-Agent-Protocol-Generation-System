from ..state import FoundryState
from .base import StateUpdate, log_agent_run
from .llm import generate_json, SYSTEM_PROMPTS


@log_agent_run("IntentInterpreter")
def run_intent_interpreter(state: FoundryState) -> StateUpdate:
    """
    Normalizes user intent using the LLM and moves the workflow into DRAFTING.
    The prompt is constrained to a single, valid JSON object so parsing
    stays robust and the notes remain concise.
    """
    user_intent = state.user_intent.strip()
    user_context = (state.user_context or "None provided").strip()

    prompt = f"""
You are analyzing a request for a CBT protocol.

User Request: "{user_intent}"
Additional Context: "{user_context}"

Your task is to normalize and structure this request so that downstream
agents can work with it easily.

Return a SINGLE JSON object and nothing else.

The JSON must have EXACTLY these keys:

{{
  "normalized_intent": "",
  "target_condition": "",
  "specific_requirements": [],
  "recommended_approach": "",
  "notes": ""
}}

Field requirements:

- "normalized_intent": 1–2 clear sentences describing what protocol
  should be generated (include key goals and modality if obvious).

- "target_condition": a short phrase naming the main problem
  (e.g., "panic disorder", "social anxiety", "insomnia", "specific phobia").

- "specific_requirements": a list (array) of SHORT strings capturing any
  explicit constraints or wishes (e.g., "no medication", "focus on exposure",
  "include sleep hygiene").

- "recommended_approach": 1–2 sentences suggesting appropriate CBT
  techniques or modules (e.g., "graded exposure", "behavioural activation").

- "notes": any brief additional considerations (e.g., risk factors,
  comorbidities, or uncertainties about the request).

Formatting rules (VERY IMPORTANT):
- Return ONLY the JSON object, with no markdown, comments, or extra text.
- Use valid JSON: double-quoted keys and string values, no trailing commas.
- Keep fields concise and avoid repetition of the full request text.
"""

    try:
        result = generate_json(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPTS["IntentInterpreter"],
            temperature=0.3,
        )

        normalized_intent = result.get("normalized_intent", "").strip() or user_intent

        # Ensure specific_requirements is always a list of strings
        raw_requirements = result.get("specific_requirements", [])
        if isinstance(raw_requirements, str):
            specific_requirements = [raw_requirements]
        else:
            specific_requirements = [
                str(item) for item in (raw_requirements or []) if str(item).strip()
            ]

        target_condition = result.get("target_condition", "").strip() or "Unknown"
        recommended_approach = (
            result.get("recommended_approach", "Standard CBT").strip()
            or "Standard CBT"
        )
        extra_notes = result.get("notes", "").strip()

        notes = (
            f"Target: {target_condition}\n"
            f"Approach: {recommended_approach}\n"
            f"Requirements: {', '.join(specific_requirements) if specific_requirements else 'None'}\n"
            f"Notes: {extra_notes}"
        )

    except Exception as e:
        # Fallback to simple normalization if LLM fails
        print(f"[IntentInterpreter] LLM call failed: {e}")
        normalized_intent = user_intent
        notes = f"Normalized (fallback): {normalized_intent}"

    new_notes = state.scratchpads.notes.copy()
    new_notes["IntentInterpreter"] = notes

    return {
        "user_intent": normalized_intent,
        "scratchpads": {"notes": new_notes},
        "status": "DRAFTING",
    }
