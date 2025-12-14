from uuid import uuid4
from ..state import FoundryState, Review
from .base import StateUpdate, log_agent_run
from .llm import generate_json, SYSTEM_PROMPTS


@log_agent_run("ClinicalCritic")
def run_clinical_critic(state: FoundryState) -> StateUpdate:
    """
    Evaluates the draft for clinical validity and CBT best practices using an LLM.
    The LLM is instructed to return a SINGLE, concise JSON object so that
    downstream parsing stays robust and the UI remains readable.
    """
    if not state.current_draft:
        return {}

    prompt = f"""
You are a CBT clinical supervisor reviewing a draft protocol.

Target Condition: "{state.user_intent}"

Protocol Draft:
---
{state.current_draft.content}
---

Your task is to evaluate the protocol's clinical validity and CBT quality
and return a SINGLE JSON object. Do not include any text before or after the JSON.

The JSON must have EXACTLY these keys:

{{
  "clinical_score": 0.0,
  "summary": "",
  "strengths": [],
  "gaps": [],
  "evidence_base": "",
  "rationale": ""
}}

Field requirements (follow these strictly):

- "clinical_score": a float between 0.0 and 1.0
  (1.0 = excellent CBT validity, 0.0 = clinically unsound).

- "summary": 1–2 concise sentences giving the overall clinical assessment.

- "strengths": 2–5 SHORT bullet points (each <= 20 words)
  describing what is clinically sound or well-structured.

- "gaps": 2–5 SHORT bullet points (each <= 20 words)
  describing missing or weak clinical elements and suggested improvements.

- "evidence_base": 1–3 sentences connecting the protocol to CBT principles.
  No formal citations or long literature reviews.

- "rationale": 3–6 sentences (<= 150 words) explaining why you chose
  the clinical_score, referring to the most important strengths and gaps.

Important formatting rules:
- Return ONLY the JSON object, with no markdown, headings, or commentary.
- Use valid JSON: double-quoted keys and string values, no comments, no trailing commas.
- Do NOT repeat the full protocol text in any field.
- Be concise and specific, not verbose.
"""

    try:
        result = generate_json(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPTS["ClinicalCritic"],
            temperature=0.2,
        )

        # Safely coerce and clamp the score
        score_raw = result.get("clinical_score", 0.9)
        try:
            score = float(score_raw)
        except (TypeError, ValueError):
            score = 0.9
        score = max(0.0, min(1.0, score))

        summary = result.get("summary", "Clinical assessment")
        strengths = result.get("strengths", []) or []
        gaps = result.get("gaps", []) or []
        evidence = result.get("evidence_base", "") or ""
        rationale = result.get("rationale", "No detailed rationale provided.") or ""

        # Build a single, compact rationale field for the Review object
        full_rationale = rationale.strip()
        if evidence:
            full_rationale += f"\n\nEvidence Base: {evidence.strip()}"
        if strengths:
            full_rationale += "\n\nClinical Strengths:\n" + "\n".join(
                f"- {s}" for s in strengths
            )
        if gaps:
            full_rationale += "\n\nClinical Gaps:\n" + "\n".join(
                f"- {g}" for g in gaps
            )

    except Exception as e:
        print(f"[ClinicalCritic] LLM call failed: {e}")
        score = 0.9
        summary = "Clinical Assessment (fallback)"
        full_rationale = (
            "Unable to perform detailed clinical analysis. "
            f"Using fallback score. Error: {str(e)}"
        )

    review = Review(
        id=str(uuid4()),
        agent_name="ClinicalCritic",
        target_draft_id=state.current_draft.id,
        summary=summary,
        line_level_comments=[],
        clinical_score=score,
        rationale=full_rationale,
    )

    # Return only this agent's review as a single-element list.
    # The merge_reviews reducer will combine all parallel reviews.
    return {
        "reviews": [review],
        "clinical_score": score,
    }
