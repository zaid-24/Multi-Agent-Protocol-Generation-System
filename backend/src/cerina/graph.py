from typing import Dict, Any, Literal, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph as CompiledGraph
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .state import FoundryState
from .agents.intent import run_intent_interpreter
from .agents.drafting import run_drafting_agent
from .agents.safety import run_safety_guardian
from .agents.empathy import run_empathy_tone_agent
from .agents.clinical import run_clinical_critic
from .agents.revision import run_revision_agent

def run_supervisor(state: FoundryState) -> Dict[str, Any]:
    """
    Orchestrates the workflow based on agent feedback and iteration counts.
    Decides whether to revise, approve (await human), or fail.
    """
    # Thresholds
    SAFETY_THRESHOLD = 0.7
    EMPATHY_THRESHOLD = 0.6
    CLINICAL_THRESHOLD = 0.6
    
    # 1. Critical Safety Check
    if state.safety_score is not None and state.safety_score < 0.2:
         return {
             "status": "FAILED", 
             "error": "Critical safety violation detected.",
             "approve_after_revision": False
         }
    
    # 2. Check for Approval readiness
    scores_present = (
        state.safety_score is not None and 
        state.empathy_score is not None and 
        state.clinical_score is not None
    )
    
    scores_passing = (
        scores_present and
        state.safety_score >= SAFETY_THRESHOLD and
        state.empathy_score >= EMPATHY_THRESHOLD and
        state.clinical_score >= CLINICAL_THRESHOLD
    )
    
    # 3. "Approve & Continue Agents" mode
    # Only check AFTER at least one revision has completed (status becomes "REVIEWING")
    if state.approve_after_revision and state.status == "REVIEWING":
        if scores_passing:
            return {
                "status": "APPROVED",
                "approve_after_revision": False
            }
        elif state.iteration >= state.max_iterations:
            return {
                "status": "FAILED",
                "error": "Max iterations reached without meeting quality thresholds.",
                "approve_after_revision": False
            }
        # Otherwise, continue revising (no state change needed)
        return {}
    
    # 4. Normal flow: check if ready for human review
    if scores_passing and state.iteration >= 1:
        return {}

    # 5. Check max iterations
    if state.iteration >= state.max_iterations:
        if not scores_passing:
            return {
                "status": "FAILED",
                "error": "Max iterations reached without meeting quality thresholds."
            }
    
    return {}

def await_human(state: FoundryState) -> Dict[str, Any]:
    """
    Halts execution and waits for human input.
    """
    return {"status": "AWAITING_HUMAN"}

def route_supervisor(state: FoundryState) -> Literal["await_human", "revision", "FAILED", "approved"]:
    """
    Determines the next node after supervisor.
    """
    if state.status == "FAILED":
        return "FAILED"
    
    if state.status == "APPROVED":
        return "approved"
    
    # Check if we should move to revising based on explicit status
    if state.status == "REVISING":
        return "revision"

    # Thresholds
    SAFETY_THRESHOLD = 0.7
    EMPATHY_THRESHOLD = 0.6
    CLINICAL_THRESHOLD = 0.6
    
    scores_present = (
        state.safety_score is not None and 
        state.empathy_score is not None and 
        state.clinical_score is not None
    )
    
    scores_passing = (
        scores_present and
        state.safety_score >= SAFETY_THRESHOLD and
        state.empathy_score >= EMPATHY_THRESHOLD and
        state.clinical_score >= CLINICAL_THRESHOLD
    )
    
    # Handle REJECTED status - end immediately
    if state.status == "REJECTED":
        return "rejected"
    
    # "Approve & Continue Agents" mode: skip human review, auto-approve when ready
    # Only check AFTER at least one revision has completed (status becomes "REVIEWING")
    if state.approve_after_revision and state.status == "REVIEWING":
        if scores_passing:
            return "approved"
        elif state.iteration < state.max_iterations:
            return "revision"
        else:
            return "FAILED"
    
    # Normal flow: wait for human when scores pass
    if scores_passing and state.iteration >= 1:
        return "await_human"
    
    if state.iteration < state.max_iterations:
        return "revision"
        
    return "FAILED"

def build_graph(checkpointer: Optional[BaseCheckpointSaver] = None) -> CompiledGraph:
    """
    Builds the LangGraph state graph with PARALLEL critic execution.
    
    Graph Structure:
    ================
    
    1. Initial Flow:
       intent_interpreter → drafting → [safety, empathy, clinical] (PARALLEL) → supervisor
    
    2. Supervisor Decision:
       supervisor → await_human (if scores pass, wait for human)
                 → revision (if scores need improvement)
                 → END (APPROVED or FAILED)
    
    3. Revision Loop:
       revision → [safety, empathy, clinical] (PARALLEL) → supervisor
    
    4. Human-in-the-Loop:
       await_human (INTERRUPTED) → supervisor (on resume)
    
    The critics (SafetyGuardian, EmpathyToneAgent, ClinicalCritic) run in parallel.
    Each returns {"reviews": [its_review], "X_score": score}.
    The merge_reviews reducer in FoundryState combines all reviews automatically.
    """
    builder = StateGraph(FoundryState)
    
    # Add Nodes
    builder.add_node("intent_interpreter", run_intent_interpreter)
    builder.add_node("drafting", run_drafting_agent)
    builder.add_node("safety", run_safety_guardian)
    builder.add_node("empathy", run_empathy_tone_agent)
    builder.add_node("clinical", run_clinical_critic)
    builder.add_node("revision", run_revision_agent)
    builder.add_node("supervisor", run_supervisor)
    builder.add_node("await_human", await_human)
    
    # Set Entry Point
    builder.set_entry_point("intent_interpreter")
    
    # ==========================================
    # INITIAL FLOW: Drafting → Parallel Critics
    # ==========================================
    builder.add_edge("intent_interpreter", "drafting")
    
    # Fan-out: Drafting triggers all three critics in PARALLEL
    builder.add_edge("drafting", "safety")
    builder.add_edge("drafting", "empathy")
    builder.add_edge("drafting", "clinical")
    
    # Fan-in: All three critics converge to supervisor
    builder.add_edge("safety", "supervisor")
    builder.add_edge("empathy", "supervisor")
    builder.add_edge("clinical", "supervisor")
    
    # ==========================================
    # SUPERVISOR: Conditional routing
    # ==========================================
    builder.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "await_human": "await_human",
            "revision": "revision",
            "FAILED": END,
            "approved": END,
            "rejected": END
        }
    )
    
    # ==========================================
    # REVISION LOOP: Revision → Parallel Critics
    # ==========================================
    builder.add_edge("revision", "safety")
    builder.add_edge("revision", "empathy")
    builder.add_edge("revision", "clinical")
    # (Critics already have edges to supervisor from above)
    
    # ==========================================
    # HUMAN-IN-THE-LOOP: Resume path
    # ==========================================
    builder.add_edge("await_human", "supervisor")
    
    # Compile with interrupt after await_human for human review
    return builder.compile(checkpointer=checkpointer, interrupt_after=["await_human"])

async def run_full_session(initial_state: FoundryState, thread_id: str = None, resume_input: dict = None) -> FoundryState:
    """
    Runs the graph until completion (END) or halt.
    
    If resume_input is provided, it resumes the graph from the last checkpoint
    using that input (Command in newer LangGraph, or just updating state).
    """
    if not thread_id:
        thread_id = initial_state.session_id
    
    # Use a local file path
    db_path = "cerina_graph.db"
    
    async with AsyncSqliteSaver.from_conn_string(db_path) as checkpointer:
        graph = build_graph(checkpointer=checkpointer)
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # If resuming, we usually pass None as input if we just want to continue,
        # or a Command/update if we want to change state.
        # Since we modify state outside (in API) before calling this, 
        # we can just invoke with None (or empty dict) to resume.
        # HOWEVER, if we are starting fresh, we pass initial_state.
        
        input_data = initial_state if not resume_input else None
        
        # NOTE: In LangGraph with checkpointer, invoking with same thread_id 
        # resumes from last checkpoint.
        # If input_data is provided (initial_state), it might reset or merge depending on config.
        # But `ainvoke` typically runs from current state.
        # If we want to resume, we pass Command(resume=...) or just null input?
        # Actually, if we pass a state update, it merges.
        
        if resume_input:
             # We are resuming. We might need to pass `None` to just "tick" the graph
             # or pass the state update if we made one.
             # But the API handler will have updated the state in DB? 
             # No, the API handler usually updates state via `update_state` or similar, 
             # OR we pass the update here.
             
             # Let's assume the API handler calls `graph.update_state` OR passes the new values here.
             # We'll support passing dictionary updates here.
             input_to_use = resume_input
        else:
             input_to_use = initial_state

        result = await graph.ainvoke(input_to_use, config=config)
        
        if isinstance(result, dict):
            return FoundryState(**result)
        return result
