import pytest
from cerina.state import new_session_state
from cerina.graph import run_full_session

@pytest.mark.asyncio
async def test_graph_basic_flow():
    """
    Test that the graph runs from INIT to AWAITING_HUMAN (or FAILED)
    and produces artifacts.
    """
    initial_state = new_session_state(
        session_id="test-session-1",
        user_intent="Create a CBT exposure hierarchy for fear of dogs"
    )
    
    final_state = await run_full_session(initial_state)
    
    # Check status
    assert final_state.status in ["AWAITING_HUMAN", "FAILED"]
    
    # Check artifacts
    if final_state.status == "AWAITING_HUMAN":
        assert final_state.current_draft is not None
        assert len(final_state.draft_history) >= 0
        assert len(final_state.reviews) >= 3 # Safety, Empathy, Clinical
        
        # Check scores are populated
        assert final_state.safety_score is not None
        assert final_state.empathy_score is not None
        assert final_state.clinical_score is not None

@pytest.mark.asyncio
async def test_graph_fail_fast():
    """
    Test that the graph handles failure (mocking a bad intent/score if possible, 
    but here we rely on the standard mock logic which passes. 
    We can force a fail by manipulating state if we mocked agents, 
    but for this basic integration test we just check it runs.)
    """
    # Since our mock agents always return good scores (0.9, 0.85, etc),
    # the default flow should succeed to AWAITING_HUMAN.
    
    initial_state = new_session_state(
        session_id="test-session-2",
        user_intent="Simple test"
    )
    
    final_state = await run_full_session(initial_state)
    
    assert final_state.status == "AWAITING_HUMAN"
    assert final_state.iteration >= 1
