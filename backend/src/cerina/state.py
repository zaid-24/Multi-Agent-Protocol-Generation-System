import operator
from typing import Annotated, List, Dict, Optional, Literal, Union, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

# --- Reducers for Parallel State Updates ---

def merge_reviews(current: List["Review"], new: List["Review"]) -> List["Review"]:
    """
    Reducer for the reviews field.
    When multiple critic agents run in parallel and each returns {"reviews": [review]},
    this reducer concatenates all reviews into a single list.
    
    Args:
        current: The existing list of reviews in the state
        new: The new list of reviews from a parallel node
        
    Returns:
        Combined list of all reviews
    """
    if current is None:
        current = []
    if new is None:
        new = []
    return current + new

# --- Data Models ---

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent_name: str
    target_draft_id: str
    summary: str
    line_level_comments: List[Dict[str, str]] = Field(default_factory=list) # {section_id, comment}
    # Scores are optional because not all reviewers give all scores
    safety_score: Optional[float] = None
    empathy_score: Optional[float] = None
    clinical_score: Optional[float] = None
    rationale: str

class Draft(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str  # agent name
    parent_draft_id: Optional[str] = None
    version_number: int = 1

class AgentScratchpad(BaseModel):
    # Using a dict to store freeform notes per agent: {"SafetyGuardian": "Detected risk..."}
    notes: Dict[str, str] = Field(default_factory=dict)

# --- Graph State ---

class FoundryState(BaseModel):
    # Session Identity
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_intent: str
    user_context: Optional[str] = None

    # Artifacts
    current_draft: Optional[Draft] = None
    draft_history: List[Draft] = Field(default_factory=list)
    
    # Reviews list with reducer for parallel critic agents.
    # When SafetyGuardian, EmpathyToneAgent, and ClinicalCritic run in parallel,
    # each returns {"reviews": [their_review]}. The merge_reviews reducer
    # concatenates all reviews so no data is lost during fan-in.
    reviews: Annotated[List[Review], merge_reviews] = Field(default_factory=list)

    # Aggregated Metrics (The "Grade")
    safety_score: Optional[float] = None
    empathy_score: Optional[float] = None
    clinical_score: Optional[float] = None

    # Flow Control
    iteration: int = 0
    max_iterations: int = 4
    status: Literal[
        "INIT",
        "DRAFTING",
        "REVIEWING", # The parallel critique phase
        "REVISING",
        "AWAITING_HUMAN",
        "APPROVED",
        "FAILED",
        "REJECTED"
    ] = "INIT"
    
    # Flag to auto-approve after the current revision cycle completes
    approve_after_revision: bool = False

    error: Optional[str] = None
    scratchpads: AgentScratchpad = Field(default_factory=AgentScratchpad)

    # Helper to easily add a note
    def add_note(self, agent: str, note: str):
        self.scratchpads.notes[agent] = note

def new_session_state(session_id: str, user_intent: str, user_context: Optional[str] = None) -> FoundryState:
    return FoundryState(
        session_id=session_id,
        user_intent=user_intent,
        user_context=user_context,
        iteration=0,
        status="INIT",
        scratchpads=AgentScratchpad(notes={})
    )

