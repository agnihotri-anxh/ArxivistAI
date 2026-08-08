import json
import time
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
METADATA_PATH = DATA_DIR / "metadata.json"
JSON_DIR = DATA_DIR / "structured_json"

PDF_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR.mkdir(parents=True, exist_ok=True)

def download_pdf(paper_id: str, pdf_url: str, output_path: Path):
    if output_path.exists() and output_path.stat().st_size > 0:
        return True
        
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    if "arxiv.org/abs/" in pdf_url:
        pdf_url = pdf_url.replace("arxiv.org/abs/", "arxiv.org/pdf/")
    if "arxiv.org/pdf/" in pdf_url and not pdf_url.endswith(".pdf"):
        pdf_url = f"{pdf_url}.pdf"
        
    for attempt in range(3):
        try:
            print(f"Downloading {paper_id}...")
            resp = requests.get(pdf_url, headers=headers, timeout=30)
            if resp.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                time.sleep(1.0)
                return True
            else:
                print(f"HTTP {resp.status_code} for {paper_id}")
                time.sleep(2 * (attempt + 1))
        except Exception as e:
            print(f"Download error: {e}")
            time.sleep(2 * (attempt + 1))
    return False

def main(max_records=None):
    if not METADATA_PATH.exists():
        print(f"Error: metadata.json not found at {METADATA_PATH}")
        return
        
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    print(f"Loaded {len(metadata)} papers from metadata.json.")
    
    downloaded_count = 0
    for paper_id, data in metadata.items():
        if max_records is not None and downloaded_count >= max_records:
            print(f"Reached batch limit of {max_records} PDF downloads.")
            break
            
        json_path = JSON_DIR / f"{paper_id}.json"
        pdf_path = PDF_DIR / f"{paper_id}.pdf"
        
        if json_path.exists() or (pdf_path.exists() and pdf_path.stat().st_size > 0):
            continue
            
        pdf_url = data.get("pdf_url")
        if not pdf_url:
            continue
            
        success = download_pdf(paper_id, pdf_url, pdf_path)
        if success:
            downloaded_count += 1
            
    print(f"\nPhase 1 (Download) Complete! Downloaded {downloaded_count} PDFs.")

if __name__ == "__main__":
    main()
