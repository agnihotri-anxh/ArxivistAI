from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from typing import Optional
from pydantic import BaseModel
from .auth import get_current_user
from ..services.agent import run_agentic_rag
from ..services.daily_sync import run_daily_sync
from ..services.paper_service import get_website_papers

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user = Depends(get_current_user)):
    try:
        # Run the agentic workflow
        answer = run_agentic_rag(request.question)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/papers")
async def list_papers(
    category: Optional[str] = Query(None),
    year: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=2000)
):
    try:
        return get_website_papers(category=category, year=year, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def trigger_daily_sync(background_tasks: BackgroundTasks):
    """
    Triggers the background daily sync pipeline to process new PDFs.
    """
    background_tasks.add_task(run_daily_sync)
    return {"message": "Daily sync triggered in the background."}
