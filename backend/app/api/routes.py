from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from .auth import get_current_user
from ..services.agent import run_agentic_rag
from ..services.daily_sync import run_daily_sync
from ..services.paper_service import get_website_papers
from ..services.chat_service import (
    get_user_chat_sessions,
    create_chat_session,
    get_chat_session,
    add_message_to_chat,
    delete_chat_session
)

router = APIRouter()

class ChatRequest(BaseModel):
    chat_id: Optional[str] = None
    question: str

class ChatResponse(BaseModel):
    chat_id: str
    answer: str
    message_id: Optional[str] = None

class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Research Chat"

# --- Chat Sessions & Conversational Memory Routes ---

@router.get("/chat/sessions")
def list_chat_sessions(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["username"]
        return get_user_chat_sessions(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/sessions")
def create_new_chat_session(request: CreateSessionRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["username"]
        return create_chat_session(user_id, title=request.title or "New Research Chat")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions/{chat_id}")
def get_single_chat_session(chat_id: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["username"]
        session = get_chat_session(chat_id, user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/sessions/{chat_id}")
def delete_single_chat_session(chat_id: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["username"]
        success = delete_chat_session(chat_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat session not found or already deleted")
        return {"message": "Chat session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["username"]
        chat_id = request.chat_id
        
        # 1. Get or create chat session
        session = None
        if chat_id:
            session = get_chat_session(chat_id, user_id)
            
        if not session:
            session = create_chat_session(user_id, title="New Research Chat")
            chat_id = session["chat_id"]

        # 2. Extract existing message history
        existing_messages = session.get("messages", [])
        history = [{"role": m["role"], "content": m["content"]} for m in existing_messages if m.get("role") in ["user", "assistant"]]
        
        # 3. Run Agentic RAG workflow passing historical context
        answer = run_agentic_rag(request.question, history=history)
        
        # 4. Save user question & assistant answer to chat session in MongoDB
        add_message_to_chat(chat_id, user_id, "user", request.question)
        msg_entry = add_message_to_chat(chat_id, user_id, "assistant", answer)
        
        return ChatResponse(
            chat_id=chat_id,
            answer=answer,
            message_id=msg_entry.get("id")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Papers Catalog Route ---

@router.get("/papers")
async def list_papers(
    category: Optional[str] = Query(None),
    year: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=500)
):
    try:
        return get_website_papers(
            category=category,
            year=year,
            search=search,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def trigger_daily_sync(background_tasks: BackgroundTasks):
    """Triggers the background daily sync pipeline to process new PDFs."""
    background_tasks.add_task(run_daily_sync)
    return {"message": "Daily sync triggered in the background."}
