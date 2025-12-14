from uuid import uuid4
from ..state import FoundryState, Review
from .base import StateUpdate, log_agent_run
from .llm import generate_json, SYSTEM_PROMPTS


@log_agent_run("SafetyGuardian")
def run_safety_guardian(state: FoundryState) -> StateUpdate:
    """
    Evaluates the draft for safety concerns using the LLM.

    Goals:
    - Identify potential harm, pacing problems, and missing crisis guidance.
    - Produce a concise, structured JSON payload (score + key concerns).
    - Keep rationale short and readable for the UI.
    """
    if not state.current_draft:
        return {}

    prompt = f"""
You are a clinical safety reviewer for CBT treatment protocols.

Target Condition: "{state.user_intent}"

Protocol Draft:
---
{state.current_draft.content}
---

Your task is to:
- Identify safety risks, contraindications, and pacing issues.
- Check for missing crisis/safety guidance.
- Rate the overall safety of this protocol.

Return a SINGLE JSON object and nothing else.

The JSON must have EXACTLY these keys:

{{
  "safety_score": 0.0,
  "summary": "",
  "concerns": [],
  "recommendations": [],
  "rationale": ""
}}

Field requirements:

- "safety_score": a float between 0.0 and 1.0
  (1.0 = completely safe and well-scaffolded,
   0.5 = usable with significant caution,
   0.0 = clearly dangerous or inappropriate).

- "summary": 1–2 concise sentences giving the overall safety assessment.

- "concerns": 0–6 SHORT bullet points (each <= 25 words)
  listing specific safety issues (e.g., "Exposure jumps too quickly from mild to extreme").

- "recommendations": 1–6 SHORT bullet points (each <= 25 words)
  with concrete safety improvements (e.g., "Add crisis line info", "Slow down hierarchy progression").

- "rationale": 3–6 sentences (<= 150 words) explaining why you chose
  the safety_score, referencing the most important concerns and recommendations.

Formatting rules (VERY IMPORTANT):
- Return ONLY the JSON object, with no markdown, headings, or extra text.
- Use valid JSON: double-quoted keys and string values, no comments, no trailing commas.
- Do NOT repeat the full protocol text in any field.
- Be direct, practical, and concise.
"""

    try:
        result = generate_json(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPTS["SafetyGuardian"],
            temperature=0.2,
        )

        # Parse and clamp safety_score safely
        score_raw = result.get("safety_score", 0.8)
        try:
            score = float(score_raw)
        except (TypeError, ValueError):
            score = 0.8
        score = max(0.0, min(1.0, score))

        summary = result.get("summary", "Safety Assessment") or "Safety Assessment"

        # Ensure concerns and recommendations are lists of strings
        concerns = result.get("concerns", []) or []
        if isinstance(concerns, str):
            concerns = [concerns]
        else:
            concerns = [str(c) for c in concerns if str(c).strip()]

        recommendations = result.get("recommendations", []) or []
        if isinstance(recommendations, str):
            recommendations = [recommendations]
        else:
            recommendations = [str(r) for r in recommendations if str(r).strip()]

        rationale = result.get("rationale", "No detailed rationale provided.") or (
            "No detailed rationale provided."
        )

        # Build a compact rationale for the Review
        full_rationale = rationale.strip()
        if concerns:
            full_rationale += "\n\nConcerns:\n" + "\n".join(f"- {c}" for c in concerns)
        if recommendations:
            full_rationale += "\n\nRecommendations:\n" + "\n".join(
                f"- {r}" for r in recommendations
            )

    except Exception as e:
        print(f"[SafetyGuardian] LLM call failed: {e}")
        score = 0.8  # Default moderately safe score
        summary = "Safety Assessment (fallback)"
        full_rationale = (
            "Unable to perform detailed safety analysis. "
            f"Using fallback score. Error: {str(e)}"
        )

    review = Review(
        id=str(uuid4()),
        agent_name="SafetyGuardian",
        target_draft_id=state.current_draft.id,
        summary=summary,
        line_level_comments=[],
        safety_score=score,
        rationale=full_rationale,
    )

    # Return only this agent's review as a single-element list.
    # The merge_reviews reducer will combine all parallel reviews.
    return {
        "reviews": [review],
        "safety_score": score,
    }
