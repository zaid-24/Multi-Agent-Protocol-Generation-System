import pytest
from cerina.state import new_session_state, FoundryState, Draft
from cerina.agents.safety import run_safety_guardian
from cerina.agents.empathy import run_empathy_tone_agent
from cerina.agents.clinical import run_clinical_critic
from cerina.agents.base import now_utc

@pytest.fixture
def state_with_draft():
    state = new_session_state("test-session-review", "Test Intent")
    state.status = "REVIEWING"
    state.current_draft = Draft(
        content="This is a safe and structured CBT protocol.",
        created_by="DraftingAgent",
        created_at=now_utc()
    )
    return state

def test_safety_guardian(state_with_draft):
    update = run_safety_guardian(state_with_draft)
    
    # Check Update content
    assert "safety_score" in update
    assert update["safety_score"] > 0.9
    assert len(update["reviews"]) == 1
    assert update["reviews"][0].agent_name == "SafetyGuardian"
    
    # Simulate Unsafe
    state_with_draft.current_draft.content = "This text is unsafe."
    update_unsafe = run_safety_guardian(state_with_draft)
    assert update_unsafe["safety_score"] < 0.5

def test_empathy_agent(state_with_draft):
    update = run_empathy_tone_agent(state_with_draft)
    
    assert "empathy_score" in update
    assert update["empathy_score"] > 0
    assert len(update["reviews"]) == 1
    assert update["reviews"][0].agent_name == "EmpathyToneAgent"

def test_clinical_critic(state_with_draft):
    update = run_clinical_critic(state_with_draft)
    
    assert "clinical_score" in update
    assert update["clinical_score"] > 0
    assert len(update["reviews"]) == 1
    assert update["reviews"][0].agent_name == "ClinicalCritic"

