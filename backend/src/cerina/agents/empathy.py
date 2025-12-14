from uuid import uuid4
from ..state import FoundryState, Review
from .base import StateUpdate, log_agent_run
from .llm import generate_json, SYSTEM_PROMPTS


@log_agent_run("EmpathyToneAgent")
def run_empathy_tone_agent(state: FoundryState) -> StateUpdate:
    """
    Evaluates the draft for empathy and therapeutic tone using an LLM.
    The prompt enforces a small, JSON-only response to avoid verbose,
    messy outputs.
    """
    if not state.current_draft:
        return {}

    prompt = f"""
You are a CBT therapist evaluating the EMPATHY and THERAPEUTIC TONE of a protocol.

Target concern: "{state.user_intent}"

Protocol Draft:
---
{state.current_draft.content}
---

Assess the following dimensions:
1. Warmth and validation
2. Non-judgmental language
3. Hope and encouragement
4. Self-efficacy messaging
5. Cultural sensitivity and inclusivity
6. Accessibility of language
7. Motivational elements
8. Therapeutic alliance building

Return a SINGLE JSON object and nothing else.

The JSON must have EXACTLY these keys:

{{
  "empathy_score": 0.0,
  "summary": "",
  "strengths": [],
  "improvements": [],
  "rationale": ""
}}

Field requirements:

- "empathy_score": float between 0.0 and 1.0
  (1.0 = excellent empathy and warmth, 0.0 = cold/harsh/invalidating).

- "summary": 1–2 concise sentences giving the overall tone assessment.

- "strengths": 2–5 SHORT bullet points (each <= 20 words)
  describing what the protocol does well in terms of empathy and tone.

- "improvements": 2–5 SHORT bullet points (each <= 20 words)
  describing concrete ways to make the tone more empathetic or accessible.

- "rationale": 3–6 sentences (<= 120 words) explaining why you chose
  the empathy_score, referring to the most important strengths and improvements.

Formatting rules (VERY IMPORTANT):
- Return ONLY the JSON object, with no markdown, headings, or extra text.
- Use valid JSON: double-quoted keys and string values, no comments, no trailing commas.
- Do NOT repeat the full protocol text in any field.
- Be specific and concise, not verbose.
"""

    try:
        result = generate_json(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPTS["EmpathyToneAgent"],
            temperature=0.2,
        )

        # Parse and clamp empathy_score safely
        score_raw = result.get("empathy_score", 0.85)
        try:
            score = float(score_raw)
        except (TypeError, ValueError):
            score = 0.85
        score = max(0.0, min(1.0, score))

        summary = result.get("summary", "Tone Assessment") or "Tone Assessment"

        strengths = result.get("strengths", []) or []
        if isinstance(strengths, str):
            strengths = [strengths]

        improvements = result.get("improvements", []) or []
        if isinstance(improvements, str):
            improvements = [improvements]

        rationale = result.get("rationale", "No detailed rationale provided.") or "No detailed rationale provided."

        full_rationale = rationale.strip()
        if strengths:
            full_rationale += "\n\nStrengths:\n" + "\n".join(f"- {s}" for s in strengths)
        if improvements:
            full_rationale += "\n\nAreas for improvement:\n" + "\n".join(
                f"- {i}" for i in improvements
            )

    except Exception as e:
        print(f"[EmpathyToneAgent] LLM call failed: {e}")
        score = 0.85
        summary = "Tone Assessment (fallback)"
        full_rationale = (
            "Unable to perform detailed empathy analysis. "
            f"Using fallback score. Error: {str(e)}"
        )

    review = Review(
        id=str(uuid4()),
        agent_name="EmpathyToneAgent",
        target_draft_id=state.current_draft.id,
        summary=summary,
        line_level_comments=[],
        empathy_score=score,
        rationale=full_rationale,
    )

    # Return only this agent's review as a single-element list.
    # The merge_reviews reducer will combine all parallel reviews.
    return {
        "reviews": [review],
        "empathy_score": score,
    }
