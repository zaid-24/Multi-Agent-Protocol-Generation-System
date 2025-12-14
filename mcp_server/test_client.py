"""
Simple test script to verify the Cerina backend API works 
(simulating what the MCP tool does).

This can be run standalone without the MCP server to verify the backend integration.
"""

import asyncio
import httpx

BACKEND_URL = "http://127.0.0.1:8000"


async def test_generate_protocol(prompt: str, context: str = None):
    """Test the full flow: create session, poll, auto-approve, get result."""
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        print(f"Creating session with prompt: {prompt}")
        
        # 1. Create session
        create_response = await client.post(
            f"{BACKEND_URL}/sessions",
            json={"user_intent": prompt, "user_context": context}
        )
        create_response.raise_for_status()
        session_data = create_response.json()
        session_id = session_data["session_id"]
        status = session_data["status"]
        
        print(f"Session created: {session_id}, Status: {status}")
        
        # 2. If awaiting human, auto-approve
        if status == "AWAITING_HUMAN":
            print("Session awaiting human approval. Auto-approving...")
            
            state_response = await client.get(f"{BACKEND_URL}/sessions/{session_id}/state")
            state_response.raise_for_status()
            state = state_response.json()
            
            current_content = state.get("current_draft", {}).get("content", "")
            
            approve_response = await client.post(
                f"{BACKEND_URL}/sessions/{session_id}/human_approve",
                json={
                    "new_content": current_content,
                    "action": "APPROVE_FINAL",
                    "comments": "Auto-approved via test script"
                }
            )
            approve_response.raise_for_status()
            result = approve_response.json()
            print(f"Approval result: {result}")
        
        # 3. Fetch final state
        final_state_response = await client.get(f"{BACKEND_URL}/sessions/{session_id}/state")
        final_state_response.raise_for_status()
        final_state = final_state_response.json()
        
        # 4. Print results
        print("\n" + "="*60)
        print("PROTOCOL GENERATION COMPLETE")
        print("="*60)
        print(f"Status: {final_state.get('status')}")
        print(f"Iterations: {final_state.get('iteration')}")
        print(f"Safety Score: {final_state.get('safety_score')}")
        print(f"Empathy Score: {final_state.get('empathy_score')}")
        print(f"Clinical Score: {final_state.get('clinical_score')}")
        print("\n--- Protocol Content ---\n")
        print(final_state.get("current_draft", {}).get("content", "No content"))
        print("\n" + "="*60)
        
        return final_state


if __name__ == "__main__":
    prompt = "Create a CBT exposure hierarchy for mild public speaking anxiety"
    asyncio.run(test_generate_protocol(prompt))
