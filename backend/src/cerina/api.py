from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
from uuid import uuid4
from datetime import datetime

from .state import new_session_state, FoundryState, Review, Draft
from .graph import run_full_session, build_graph
from .db import init_db
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

app = FastAPI(title="Cerina Protocol Foundry API")

# Configure CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure DB is initialized
init_db()

class CreateSessionRequest(BaseModel):
    user_intent: str
    user_context: Optional[str] = None

class CreateSessionResponse(BaseModel):
    session_id: str
    status: str

class HumanApproveRequest(BaseModel):
    new_content: str
    action: Literal["APPROVE_FINAL", "APPROVE_CONTINUE", "REQUEST_REVISION", "REJECT"]
    comments: Optional[str] = None

@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Creates a new session and runs it until human approval is needed or it completes/fails.
    """
    session_id = str(uuid4())
    initial_state = new_session_state(
        session_id=session_id,
        user_intent=request.user_intent,
        user_context=request.user_context
    )
    
    # Log session creation
    try:
        from .db import SessionLocal, RunSession
        db = SessionLocal()
        new_run = RunSession(
            id=str(uuid4()),
            session_id=session_id,
            status="INIT",
            started_at=datetime.now()
        )
        db.add(new_run)
        db.commit()
        db.close()
    except Exception as e:
        print(f"Failed to log session start: {e}")
    
    try:
        # Run the graph
        final_state = await run_full_session(initial_state)
        
        # Update session status log
        try:
            db = SessionLocal()
            run = db.query(RunSession).filter(RunSession.session_id == session_id).first()
            if run:
                run.status = final_state.status
                if final_state.status in ["APPROVED", "FAILED"]:
                    run.ended_at = datetime.now()
                db.commit()
            db.close()
        except Exception as e:
             print(f"Failed to update session log: {e}")

        return {
            "session_id": session_id,
            "status": final_state.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/human_approve")
async def human_approve(session_id: str, request: HumanApproveRequest):
    """
    Applies human edits and approval decision, then resumes the graph.
    """
    db_path = "cerina_graph.db"
    
    try:
        async with AsyncSqliteSaver.from_conn_string(db_path) as checkpointer:
            graph = build_graph(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": session_id}}
            
            # 1. Get current state
            snapshot = await graph.aget_state(config)
            if not snapshot or not snapshot.values:
                 raise HTTPException(status_code=404, detail="Session not found")
            
            current_state = FoundryState(**snapshot.values)
            
            # 2. Create a "Human Review" to log the feedback
            human_review = Review(
                id=str(uuid4()),
                agent_name="HumanReviewer",
                target_draft_id=current_state.current_draft.id if current_state.current_draft else "unknown",
                summary=f"Human Action: {request.action}",
                rationale=request.comments or "No comments provided.",
                safety_score=1.0 if request.action != "REQUEST_REVISION" else None,
                empathy_score=1.0 if request.action != "REQUEST_REVISION" else None,
                clinical_score=1.0 if request.action != "REQUEST_REVISION" else None
            )
            
            # 3. Prepare base updates - convert Pydantic objects to dicts for LangGraph
            # Serialize existing reviews + new human review
            serialized_reviews = [r.model_dump(mode='json') if hasattr(r, 'model_dump') else r for r in current_state.reviews]
            serialized_reviews.append(human_review.model_dump(mode='json'))
            
            updates: Dict[str, Any] = {
                "reviews": serialized_reviews
            }
            
            # Update draft content if changed
            if current_state.current_draft and request.new_content != current_state.current_draft.content:
                updated_draft = current_state.current_draft.model_copy(update={"content": request.new_content})
                updates["current_draft"] = updated_draft.model_dump(mode='json')
            
            # 4. Handle each action type
            if request.action == "APPROVE_FINAL":
                # Mark as approved - graph will route to END
                updates["status"] = "APPROVED"
                
            elif request.action == "APPROVE_CONTINUE":
                # Let agents do one more revision cycle, then auto-approve
                # This triggers revision -> safety -> empathy -> clinical -> supervisor -> APPROVED
                updates["status"] = "REVISING"
                updates["approve_after_revision"] = True
                
            elif request.action == "REQUEST_REVISION":
                # Send back to revision agent
                updates["status"] = "REVISING"
            
            elif request.action == "REJECT":
                # User rejected the protocol - end immediately
                updates["status"] = "REJECTED"
            
            # 5. Apply updates to state
            # Use as_node="await_human" to tell LangGraph this update is from the await_human node
            # This ensures the graph follows the await_human -> supervisor edge when resuming
            print(f"[DEBUG] Updating state with: status={updates.get('status')}")
            await graph.aupdate_state(config, updates, as_node="await_human")
            
            # 6. Resume graph execution
            print(f"[DEBUG] Resuming graph for session {session_id}")
            result = await graph.ainvoke(None, config=config)
            print(f"[DEBUG] Graph result status: {result.get('status') if isinstance(result, dict) else 'unknown'}")
            
            final_state = FoundryState(**result) if isinstance(result, dict) else result
            
            # Update the RunSession table with the new status
            try:
                from .db import SessionLocal, RunSession
                db = SessionLocal()
                run = db.query(RunSession).filter(RunSession.session_id == session_id).first()
                if run:
                    run.status = final_state.status
                    if final_state.status in ["APPROVED", "FAILED", "REJECTED"]:
                        run.ended_at = datetime.now()
                    db.commit()
                db.close()
            except Exception as db_err:
                print(f"Failed to update session log: {db_err}")
            
            return {"status": final_state.status, "session_id": session_id}

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] human_approve failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def list_sessions():
    """
    Lists all sessions from the database logs, ordered by most recent first.
    """
    try:
        from .db import SessionLocal, RunSession
        db = SessionLocal()
        
        # Query sessions ordered by started_at descending (most recent first)
        sessions = db.query(RunSession).order_by(RunSession.started_at.desc()).all()
        
        # If empty, fallback to distinct agent runs (slower but works for demo)
        if not sessions:
            from sqlalchemy import distinct
            from .db import AgentRun
            distinct_ids = db.query(distinct(AgentRun.session_id)).all()
            # Construct dummy objects (reversed to show recent first)
            return [{"session_id": row[0], "status": "UNKNOWN", "created_at": None} for row in reversed(distinct_ids)]
            
        return [{"session_id": s.session_id, "status": s.status, "created_at": s.started_at} for s in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/sessions/{session_id}/state")
async def get_session_state(session_id: str):
    """
    Retrieves the latest state for a given session from the checkpointer.
    """
    db_path = "cerina_graph.db"
    
    try:
        async with AsyncSqliteSaver.from_conn_string(db_path) as checkpointer:
            graph = build_graph(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": session_id}}
            
            snapshot = await graph.aget_state(config)
            
            if not snapshot or not snapshot.values:
                raise HTTPException(status_code=404, detail="Session not found or no state available")
                
            return snapshot.values
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read state: {str(e)}")

