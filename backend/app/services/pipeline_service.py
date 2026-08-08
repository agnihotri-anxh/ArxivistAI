import sys
import threading
import traceback
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from ..db.database import (
    get_raw_arxiv_collection,
    get_papers_collection,
    get_users_collection
)
from ..services.milvus_search import get_milvus_client, COLLECTION_NAME

# Setup path to import collector, data_prep, and vector_db modules
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

class PipelineState:
    def __init__(self):
        self.lock = threading.Lock()
        self.is_running: bool = False
        self.stop_requested: bool = False
        self.current_step: str = "Idle"
        self.last_run: str = "Never"
        self.logs: List[str] = ["Pipeline orchestrator service initialized."]
        self.status: str = "idle" # "idle", "running", "completed", "cancelled", "error"
        self.recent_processed_papers: List[Dict[str, Any]] = []

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        print(entry)
        with self.lock:
            self.logs.append(entry)
            if len(self.logs) > 500:
                self.logs = self.logs[-500:]

    def record_processed_paper(self, paper_id: str, title: str, category: str, status: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {
            "paper_id": paper_id,
            "title": title[:60] + ("..." if len(title) > 60 else "") if title else f"Document {paper_id}",
            "category": category or "Research",
            "status": status,
            "timestamp": timestamp
        }
        with self.lock:
            self.recent_processed_papers = [
                p for p in self.recent_processed_papers 
                if not (p["paper_id"] == paper_id and p["status"] == status)
            ]
            self.recent_processed_papers.insert(0, entry)
            if len(self.recent_processed_papers) > 50:
                self.recent_processed_papers = self.recent_processed_papers[:50]

    def set_running(self, step_name: str):
        with self.lock:
            self.is_running = True
            self.stop_requested = False
            self.current_step = step_name
            self.status = "running"
        self.log(f"Started pipeline step: {step_name}")

    def set_finished(self, status: str = "completed"):
        with self.lock:
            self.is_running = False
            self.stop_requested = False
            self.current_step = "Idle"
            self.status = status
            self.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log(f"Pipeline execution finished with status: {status}")

    def request_cancel(self) -> bool:
        with self.lock:
            if self.is_running:
                self.stop_requested = True
                self.log("Cancellation requested by administrator.")
                return True
        return False

pipeline_state = PipelineState()

def cancel_pipeline() -> bool:
    return pipeline_state.request_cancel()

def get_system_metrics() -> Dict[str, Any]:
    """Aggregates real-time system metrics across MongoDB and Milvus."""
    raw_coll = get_raw_arxiv_collection()
    papers_coll = get_papers_collection()
    users_coll = get_users_collection()

    raw_count = raw_coll.count_documents({})
    website_papers_count = papers_coll.count_documents({})
    users_count = users_coll.count_documents({})

    milvus_vectors_count = 0
    try:
        client = get_milvus_client()
        res = client.get_collection_stats(collection_name=COLLECTION_NAME)
        milvus_vectors_count = int(res.get("row_count", 0))
    except Exception as e:
        print(f"[Metrics] Milvus stats note: {e}")

    with pipeline_state.lock:
        logs_snapshot = list(pipeline_state.logs[-100:])
        recent_papers = list(pipeline_state.recent_processed_papers[:30])
        is_running = pipeline_state.is_running
        current_step = pipeline_state.current_step
        last_run = pipeline_state.last_run
        status = pipeline_state.status

    return {
        "raw_staging_count": raw_count,
        "website_papers_count": website_papers_count,
        "users_count": users_count,
        "milvus_vectors_count": milvus_vectors_count,
        "is_running": is_running,
        "current_step": current_step,
        "last_run": last_run,
        "status": status,
        "logs": logs_snapshot,
        "recent_processed_papers": recent_papers
    }

def _task_harvest(max_records: int = 50):
    try:
        pipeline_state.set_running(f"arXiv Harvesting (Limit: {max_records} papers)")
        mod = importlib.import_module("backend.collector.search")
        if hasattr(mod, "collect_papers"):
            mod.collect_papers(max_papers=max_records)
        pipeline_state.set_finished("completed")
    except Exception as e:
        pipeline_state.log(f"Error during harvesting: {e}\n{traceback.format_exc()}")
        pipeline_state.set_finished("error")

def _task_download(max_records: int = 50):
    try:
        pipeline_state.set_running(f"PDF Downloading (Limit: {max_records} files)")
        mod = importlib.import_module("backend.vector_db.data_prep.01_download_pdfs")
        if hasattr(mod, "main"):
            mod.main(max_records=max_records)
        pipeline_state.set_finished("completed")
    except Exception as e:
        pipeline_state.log(f"Error during PDF download: {e}\n{traceback.format_exc()}")
        pipeline_state.set_finished("error")

def _task_extract(max_records: int = 50):
    try:
        pipeline_state.set_running(f"Marker & Visual Extraction (Limit: {max_records} docs)")
        mod = importlib.import_module("backend.vector_db.data_prep.03_extract_visuals_and_compile")
        if hasattr(mod, "main"):
            mod.main(max_records=max_records)
        pipeline_state.set_finished("completed")
    except Exception as e:
        pipeline_state.log(f"Error during extraction: {e}\n{traceback.format_exc()}")
        pipeline_state.set_finished("error")

def _task_embed(max_records: int = 50):
    try:
        pipeline_state.set_running(f"Vector Embedding & Milvus Indexing (Limit: {max_records} docs)")
        mod = importlib.import_module("backend.vector_db.04_run_pipeline")
        if hasattr(mod, "main"):
            mod.main(max_records=max_records)
        pipeline_state.set_finished("completed")
    except Exception as e:
        pipeline_state.log(f"Error during vector embedding: {e}\n{traceback.format_exc()}")
        pipeline_state.set_finished("error")

def _task_full_pipeline(max_records: int = 50):
    try:
        pipeline_state.set_running(f"Full Ingestion: Harvesting ({max_records} papers)")
        harvest_mod = importlib.import_module("backend.collector.search")
        if hasattr(harvest_mod, "collect_papers"):
            harvest_mod.collect_papers(max_papers=max_records)

        pipeline_state.set_running(f"Full Ingestion: Downloading PDFs ({max_records} files)")
        download_mod = importlib.import_module("backend.vector_db.data_prep.01_download_pdfs")
        if hasattr(download_mod, "main"):
            download_mod.main(max_records=max_records)

        pipeline_state.set_running(f"Full Ingestion: Marker & Visual Extraction ({max_records} docs)")
        extract_mod = importlib.import_module("backend.vector_db.data_prep.03_extract_visuals_and_compile")
        if hasattr(extract_mod, "main"):
            extract_mod.main(max_records=max_records)

        pipeline_state.set_running(f"Full Ingestion: Vector Embedding & Milvus Indexing ({max_records} docs)")
        embed_mod = importlib.import_module("backend.vector_db.04_run_pipeline")
        embed_mod.main(max_records=max_records)

        pipeline_state.set_finished("completed")
    except Exception as e:
        pipeline_state.log(f"Error in full pipeline: {e}\n{traceback.format_exc()}")
        pipeline_state.set_finished("error")

def trigger_pipeline_step(step_type: str, max_records: int = 50) -> bool:
    """Triggers an ingestion pipeline step asynchronously in a background thread with target max_records batch size."""
    with pipeline_state.lock:
        if pipeline_state.is_running:
            return False

    pipeline_state.log(f"Requested pipeline execution with batch limit: {max_records} records.")

    target_func = None
    if step_type == "harvest":
        target_func = lambda: _task_harvest(max_records)
    elif step_type == "download":
        target_func = lambda: _task_download(max_records)
    elif step_type == "extract":
        target_func = lambda: _task_extract(max_records)
    elif step_type == "embed":
        target_func = lambda: _task_embed(max_records)
    elif step_type == "full":
        target_func = lambda: _task_full_pipeline(max_records)

    if target_func:
        thread = threading.Thread(target=target_func, daemon=True)
        thread.start()
        return True
    return False
