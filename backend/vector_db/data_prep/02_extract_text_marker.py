import subprocess
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
MD_DIR = DATA_DIR / "markdown"
FAILED_LOG = DATA_DIR / "failed_stage2.txt"

MD_DIR.mkdir(parents=True, exist_ok=True)

import os

def stage_a_marker(pdf_path: Path):
    print(f"\n--- [Stage 2] Running Marker on {pdf_path.name} ---")
    cmd = [
        "marker_single",
        str(pdf_path),
        "--output_dir", str(MD_DIR),
        "--output_format", "markdown",
        "--disable_ocr"
    ]
    print(f"Running Command: {' '.join(cmd)}")
    try:
        # Set environment variable to stop Marker from extracting images (emojis/icons)
        env = os.environ.copy()
        env["EXTRACT_IMAGES"] = "False"
        subprocess.run(cmd, check=True, env=env)
        print("Marker extraction complete.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Marker failed with error code {e.returncode}")
        return False

if __name__ == "__main__":
    pdfs = list(PDF_DIR.glob("*.pdf"))
    print(f"Found {len(pdfs)} downloaded PDFs ready for Marker extraction.")
    
    for pdf_path in pdfs:
        paper_id = pdf_path.stem
        md_file = MD_DIR / paper_id / f"{paper_id}.md"
        
        if md_file.exists():
            print(f"Skipping {paper_id} - Markdown already exists!")
            continue
            
        try:
            success = stage_a_marker(pdf_path)
            if not success:
                raise Exception("Marker failed to extract markdown.")
        except Exception as e:
            error_msg = f"Failed to process {pdf_path.name}: {e}"
            print(f"ERROR: {error_msg}")
            traceback.print_exc()
            with open(FAILED_LOG, "a", encoding="utf-8") as f:
                f.write(error_msg + "\n")
                
    print("\nPhase 2 (Marker Extraction) Complete! Check failed_stage2.txt for any errors.")
