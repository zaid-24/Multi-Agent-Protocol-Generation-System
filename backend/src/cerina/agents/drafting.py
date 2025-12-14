from uuid import uuid4
from ..state import FoundryState, Draft
from .base import StateUpdate, now_utc, log_agent_run
from .llm import generate_text, SYSTEM_PROMPTS


@log_agent_run("DraftingAgent")
def run_drafting_agent(state: FoundryState) -> StateUpdate:
    """
    Produces a concise, structured CBT protocol draft using the LLM.

    The prompt is deliberately strict to avoid overly long, messy output.
    The model is asked to return a short markdown document with clear sections,
    focusing on actionable protocol steps and (when relevant) an exposure hierarchy.
    """
    # Notes from intent interpreter, if available
    interpreter_notes = state.scratchpads.notes.get("IntentInterpreter", "")

    # Check if this is a revision (we have a current draft already)
    is_revision = state.current_draft is not None

    if is_revision:
        # Revision pass: keep structure, tighten content, incorporate notes
        prompt = f"""
You are a CBT protocol editor.

Original request: "{state.user_intent}"
Clinical context: "{state.user_context or 'None provided'}"

Intent analysis / notes:
{interpreter_notes or '(none)'}

Previous draft:
---
{state.current_draft.content}
---

Your task:
- Revise and IMPROVE this protocol.
- Make it SHORTER, clearer, and more structured.
- Remove redundant psychoeducation or repeated explanations.
- Keep only what is clinically useful and actionable.

Output format (VERY IMPORTANT):

Write markdown with EXACTLY these sections in this order:

# CBT Protocol: <short title>

## Summary
- 1–2 bullet points describing the main goal and target symptoms.

## Core CBT Steps
- 4–8 numbered steps describing the key CBT tasks in session and between sessions.
- Each step must be a single sentence (max 25 words).

## Exposure Hierarchy
- Include this section if the request involves phobia, exposure, or hierarchy.
- Use a markdown table with 6–10 rows and these columns:

| Step | Situation | Anticipated SUDS (0–100) | Target SUDS (0–100) | Notes |

Each row must be one specific, progressively more difficult situation.

## Homework
- 3–5 bullet points assigning concrete homework tasks that follow from the above.

Length & style constraints:
- TOTAL length under 450 words.
- Do NOT paste long theory lectures or definitions.
- Do NOT include worksheets or multi-page tables.
- Do NOT repeat the full request text.
- Tone: clear, professional, and supportive, but concise.
"""
    else:
        # First draft
        prompt = f"""
You are a CBT protocol draftsman.

User intent: "{state.user_intent}"
Clinical context: "{state.user_context or 'None provided'}"

Intent analysis / notes:
{interpreter_notes or '(none)'}

Your job is to produce a SHORT, STRUCTURED CBT protocol draft that another
clinician can quickly scan and use. Do NOT write a long psychoeducational handout.

Output format (VERY IMPORTANT):

Write markdown with EXACTLY these sections in this order:

# CBT Protocol: <short title>

## Summary
- 1–2 bullet points describing the main goal and target symptoms.

## Core CBT Steps
- 4–8 numbered steps describing the key CBT tasks in session and between sessions.
- Each step must be a single sentence (max 25 words).

## Exposure Hierarchy
If the intent mentions phobia, exposure, hierarchy, or avoidance, include this section.
Otherwise, include it only if graded exposure is clearly relevant.

Create a markdown table with 6–10 rows and these columns:

| Step | Situation | Anticipated SUDS (0–100) | Target SUDS (0–100) | Notes |

Each row must be one specific, progressively more difficult situation.

## Homework
- 3–5 bullet points assigning concrete homework tasks that follow from the protocol.

Length & style constraints:
- TOTAL length under 400–450 words.
- Do NOT include long theory lectures, definitions, or multi-page worksheets.
- Do NOT repeat the full user intent text.
- Focus on being concrete, graded, and clinically usable.
- Tone: clear, professional, and supportive, but concise.
"""

    try:
        protocol_content = generate_text(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPTS["DraftingAgent"],
            temperature=0.5,
            max_tokens=800,  # keep outputs compact
        )
    except Exception as e:
        print(f"[DraftingAgent] LLM call failed: {e}")
        # Fallback content
        protocol_content = f"""CBT Protocol for: {state.user_intent}

**Note: This is a fallback template. LLM generation failed.**

## Summary
- CBT protocol skeleton generated without model assistance.

## Core CBT Steps
1. Provide brief psychoeducation about the condition and CBT rationale.
2. Collaboratively identify target situations and build a graded exposure plan.
3. Teach basic cognitive restructuring (identify and challenge key thoughts).
4. Assign between-session practice and review logs in each session.

## Exposure Hierarchy
| Step | Situation                  | Anticipated SUDS (0–100) | Target SUDS (0–100) | Notes                  |
| 1    | Mildly anxiety-provoking   | 20                        | 10                  | Very safe, easy start. |
| 2    | Moderately challenging     | 40                        | 20                  | Repeat several times.  |
| 3    | Clearly difficult          | 60                        | 30                  | Stay until SUDS drops. |
| 4    | Very difficult             | 80                        | 40                  | With therapist support.|

## Homework
- Practice agreed exposure steps several times per week.
- Track SUDS before, peak, and after each exposure.
- Bring logs to the next session.

If you experience severe distress or safety concerns, contact your therapist or a crisis service.

Error details: {str(e)}"""

    new_draft = Draft(
        id=str(uuid4()),
        content=protocol_content,
        created_at=now_utc(),
        created_by="DraftingAgent",
        version_number=state.iteration + 1,
        parent_draft_id=state.current_draft.id if state.current_draft else None,
    )

    new_history = state.draft_history + (
        [state.current_draft] if state.current_draft else []
    )

    return {
        "current_draft": new_draft,
        "draft_history": new_history,
        "iteration": state.iteration + 1,
        "status": "REVIEWING",
    }
