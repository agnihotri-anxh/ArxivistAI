from fastapi import APIRouter, HTTPException, Query
from ..services.pipeline_service import get_system_metrics, trigger_pipeline_step

router = APIRouter()

@router.get("/status")
def get_admin_status():
    """Returns live system metrics, database counts, and background pipeline logs."""
    try:
        return get_system_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline/{action}")
def run_pipeline_action(action: str, limit: int = Query(50, ge=1, le=5000)):
    """
    Triggers a background ingestion pipeline action with optional batch size limit.
    Supported actions: 'harvest', 'download', 'extract', 'embed', 'full'
    """
    allowed_actions = ["harvest", "download", "extract", "embed", "full"]
    if action not in allowed_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action '{action}'. Allowed actions: {allowed_actions}"
        )

    started = trigger_pipeline_step(action, max_records=limit)
    if not started:
        raise HTTPException(
            status_code=409,
            detail="A pipeline task is currently already running. Please wait for it to complete."
        )

    return {"message": f"Pipeline step '{action}' with batch limit {limit} triggered successfully in the background."}
