from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from .auth import get_current_user
from ..services.agent import run_agentic_rag
from ..services.daily_sync import run_daily_sync
from ..services.milvus_search import get_all_papers

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
async def list_papers():
    try:
        return get_all_papers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def trigger_daily_sync(background_tasks: BackgroundTasks):
    """
    Triggers the background daily sync pipeline to process new PDFs.
    """
    background_tasks.add_task(run_daily_sync)
    return {"message": "Daily sync triggered in the background."}
