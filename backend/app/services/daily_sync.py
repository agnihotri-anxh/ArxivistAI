import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_PREP_DIR = BASE_DIR / "data_prep"

def run_daily_sync():
    """
    This background task triggers the extraction pipeline for new PDFs.
    Since 04_run_pipeline.py is idempotent, it safely inserts only new chunks into Milvus.
    """
    print("Starting Daily Sync Pipeline...")
    
    try:
        # 1. Download new PDFs based on metadata updates
        print("Step 1: Downloading new PDFs...")
        subprocess.run([sys.executable, str(DATA_PREP_DIR / "01_download_pdfs.py")], check=True)
        
        # 2. Run Marker text extraction (skips existing output folders)
        print("Step 2: Extracting Text (Marker)...")
        subprocess.run([sys.executable, str(DATA_PREP_DIR / "02_extract_text_marker.py")], check=True)
        
        # 3. Extract Visuals and Compile JSON (skips existing JSONs)
        print("Step 3: Compiling JSONs...")
        subprocess.run([sys.executable, str(DATA_PREP_DIR / "03_extract_visuals_and_compile.py")], check=True)
        
        # 4. Insert into Zilliz Cloud Vector DB (skips existing paper_ids)
        print("Step 4: Updating Milvus Vector Database...")
        subprocess.run([sys.executable, str(DATA_PREP_DIR / "vector_db" / "04_run_pipeline.py")], check=True)
        
        print("Daily Sync Pipeline Completed Successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Daily Sync Pipeline failed at step with exit code {e.returncode}")
    except Exception as e:
        print(f"An unexpected error occurred during sync: {e}")
