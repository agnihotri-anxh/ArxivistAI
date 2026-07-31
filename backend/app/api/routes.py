from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from ..services.agent import run_agentic_rag
from ..services.daily_sync import run_daily_sync

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Run the agentic workflow
        answer = run_agentic_rag(request.question)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def trigger_daily_sync(background_tasks: BackgroundTasks):
    """
    Triggers the background daily sync pipeline to process new PDFs.
    """
    background_tasks.add_task(run_daily_sync)
    return {"message": "Daily sync triggered in the background."}
