from fastapi import APIRouter, HTTPException, Query, Depends
from ..services.pipeline_service import get_system_metrics, trigger_pipeline_step, cancel_pipeline
from .auth import get_current_admin

router = APIRouter()

@router.get("/status")
def get_admin_status(admin_user: dict = Depends(get_current_admin)):
    """Returns live system metrics, database counts, recent processed papers, and background pipeline logs (Admin Only)."""
    try:
        return get_system_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline/cancel")
def cancel_active_pipeline(admin_user: dict = Depends(get_current_admin)):
    """Cancels the currently running ingestion task (Admin Only)."""
    cancelled = cancel_pipeline()
    if not cancelled:
        raise HTTPException(
            status_code=400,
            detail="No active pipeline task is currently running."
        )
    return {"message": "Pipeline cancellation requested successfully."}

@router.post("/pipeline/{action}")
def run_pipeline_action(
    action: str,
    limit: int = Query(50, ge=1, le=5000),
    admin_user: dict = Depends(get_current_admin)
):
    """
    Triggers a background ingestion pipeline action with optional batch size limit (Admin Only).
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
