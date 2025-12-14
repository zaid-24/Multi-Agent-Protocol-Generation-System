from uuid import uuid4
from ..state import FoundryState, Draft
from .base import StateUpdate, now_utc, log_agent_run
from .llm import generate_text, SYSTEM_PROMPTS


@log_agent_run("RevisionAgent")
def run_revision_agent(state: FoundryState) -> StateUpdate:
    """
    Revises the current CBT protocol draft based on reviewer feedback.

    Goals:
    - Apply safety, empathy, and clinical feedback from all reviewers.
    - Preserve the existing section structure and headings.
    - Keep the protocol concise and well-formatted markdown.
    - Avoid expanding into long psychoeducational essays.
    """
    current_draft = state.current_draft
    if not current_draft:
        return {}

    # Gather reviews for this draft
    relevant_reviews = [
        r for r in state.reviews
        if r.target_draft_id == current_draft.id
    ]

    # Format reviews for the prompt (summaries + key rationale only)
    reviews_text = ""
    for review in relevant_reviews:
        # Build a compact view of each review
        score_bits = []
        if review.safety_score is not None:
            score_bits.append(f"Safety={review.safety_score:.2f}")
        if review.empathy_score is not None:
            score_bits.append(f"Empathy={review.empathy_score:.2f}")
        if review.clinical_score is not None:
            score_bits.append(f"Clinical={review.clinical_score:.2f}")
        score_str = ", ".join(score_bits) if score_bits else "No numeric scores."

        reviews_text += f"""
### {review.agent_name}
Summary: {review.summary}
Scores: {score_str}
Key points:
{review.rationale}
"""

    # Strict, structure-preserving prompt
    prompt = f"""
You are an expert CBT protocol editor.

Original Request:
"{state.user_intent}"

Current Draft (Version {current_draft.version_number}):
---
{current_draft.content}
---

Expert Reviews (summarized):
{reviews_text if reviews_text else "No reviews available yet."}

Your job is to produce a REVISED version of the protocol that:

- Addresses ALL important concerns raised by reviewers (safety, empathy, clinical).
- Preserves the existing section structure and headings as much as possible.
- Keeps the protocol SHORT, clear, and clinically usable.
- DOES NOT add long theory lectures, multi-page psychoeducation, or new complex sections.
- Resolves obvious contradictions between reviewers in a reasonable way.

Output format (VERY IMPORTANT):
- Output MUST be valid, well-formatted MARKDOWN only.
- Keep the same overall section outline as the current draft when possible
  (e.g., Summary, Core CBT Steps, Exposure Hierarchy, Homework).
- If you add or remove a section, explain it briefly in the text (one short sentence).

Length constraints:
- TOTAL length of the revised protocol must be UNDER 600 words.
- Avoid repeating the original request or long reviewer text.
- Focus on concrete steps, clear hierarchy, and practical guidance.

Now write the revised CBT protocol in markdown, replacing the old draft.
"""

    try:
        revised_content = generate_text(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPTS["RevisionAgent"],
            temperature=0.4,
            max_tokens=900,  # keep revisions compact
        )
    except Exception as e:
        print(f"[RevisionAgent] LLM call failed: {e}")
        # Fallback: append feedback summary to the draft
        feedback_summary = "; ".join([r.summary for r in relevant_reviews]) or "No reviewer summaries."
        revised_content = (
            current_draft.content
            + f"\n\n[Revision Note: Feedback received - {feedback_summary}. "
            f"LLM revision failed: {str(e)}]"
        )

    new_draft = Draft(
        id=str(uuid4()),
        content=revised_content,
        created_at=now_utc(),
        created_by="RevisionAgent",
        version_number=current_draft.version_number + 1,
        parent_draft_id=current_draft.id,
    )

    # Move current draft to history
    new_history = state.draft_history + [current_draft]

    return {
        "current_draft": new_draft,
        "draft_history": new_history,
        "iteration": state.iteration + 1,  # Increment iteration on each revision
        "status": "REVIEWING",
    }
