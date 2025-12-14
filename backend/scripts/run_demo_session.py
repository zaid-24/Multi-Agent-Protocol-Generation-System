import sys
import os
import asyncio
import argparse
from uuid import uuid4

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from cerina.graph import run_full_session
from cerina.state import new_session_state
from cerina.db import init_db

async def main():
    # Ensure tables exist
    init_db()

    parser = argparse.ArgumentParser(description="Run a Cerina Foundry demo session.")
    parser.add_argument("--intent", type=str, default="Create a CBT exposure hierarchy for social anxiety.", help="User intent")
    parser.add_argument("--session-id", type=str, default=None, help="Session ID (optional)")
    
    args = parser.parse_args()
    
    session_id = args.session_id if args.session_id else f"demo-{str(uuid4())[:8]}"
    
    print(f"Starting session: {session_id}")
    print(f"Intent: {args.intent}")
    
    initial_state = new_session_state(
        session_id=session_id,
        user_intent=args.intent
    )
    
    try:
        final_state = await run_full_session(initial_state)
        
        print("\n=== Session Complete ===")
        print(f"Final Status: {final_state.status}")
        print(f"Drafts: {len(final_state.draft_history) + (1 if final_state.current_draft else 0)}")
        print(f"Reviews: {len(final_state.reviews)}")
        
        if final_state.status == "AWAITING_HUMAN":
            print("\n[SUCCESS] The system produced a draft and is waiting for human approval.")
        elif final_state.status == "FAILED":
            print(f"\n[FAILED] Error: {final_state.error}")
            
    except Exception as e:
        print(f"\n[ERROR] execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
