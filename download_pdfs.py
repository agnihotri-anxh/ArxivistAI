import json
import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).parent
METADATA_PATH = BASE_DIR / "data" / "metadata.json"
PDF_DIR = BASE_DIR / "data" / "pdfs"

# Configuration
# Keep MAX_WORKERS low to avoid getting IP-banned by arXiv or other sources.
# arXiv usually recommends a 3-second delay between requests for bulk downloads.
MAX_WORKERS = 3
RETRY_COUNT = 3
DELAY_BETWEEN_REQUESTS = 1.0  # seconds to sleep after a successful request or retry

def download_pdf(paper_id, pdf_url):
    # Some URLs might not end in .pdf, but we will save them as .pdf
    output_path = PDF_DIR / f"{paper_id}.pdf"
    
    # Skip if already downloaded
    if output_path.exists():
        # Check if the file is not empty
        if output_path.stat().st_size > 0:
            return paper_id, True, "Already downloaded"
        
    for attempt in range(RETRY_COUNT):
        try:
            # A common User-Agent to avoid immediate 403 Forbidden
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # If the pdf_url is just an arxiv URL without .pdf (like https://arxiv.org/pdf/2607.08768v1),
            # requests should handle it. Sometimes we might want to append .pdf to the arxiv URL.
            if "arxiv.org/abs/" in pdf_url:
                pdf_url = pdf_url.replace("arxiv.org/abs/", "arxiv.org/pdf/")
                
            if "arxiv.org/pdf/" in pdf_url and not pdf_url.endswith(".pdf"):
                pdf_url = f"{pdf_url}.pdf"
                
            response = requests.get(pdf_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                time.sleep(DELAY_BETWEEN_REQUESTS)
                return paper_id, True, "Success"
            elif response.status_code in (403, 429):
                # Rate limited or forbidden. Sleep longer before retrying.
                time.sleep(DELAY_BETWEEN_REQUESTS * (attempt + 5))
            else:
                return paper_id, False, f"HTTP {response.status_code}"
                
        except Exception as e:
            time.sleep(DELAY_BETWEEN_REQUESTS)
            if attempt == RETRY_COUNT - 1:
                return paper_id, False, str(e)
                
    return paper_id, False, "Max retries exceeded"

def main():
    # Create the pdf directory if it doesn't exist
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading metadata from {METADATA_PATH}...")
    try:
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {METADATA_PATH}")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from metadata file.")
        return

    # Extract download tasks
    tasks = []
    for paper_id, data in metadata.items():
        pdf_url = data.get("pdf_url")
        if pdf_url:
            tasks.append((paper_id, pdf_url))
            
    total_tasks = len(tasks)
    print(f"Found {total_tasks} PDFs to download.")
    if total_tasks == 0:
        return
    
    # Try importing tqdm for a nice progress bar, otherwise fallback to simple print
    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        has_tqdm = False
        print("Tip: Install 'tqdm' (`pip install tqdm`) for a progress bar.")
        
    successful = 0
    failed = 0
    
    print(f"Starting downloads with {MAX_WORKERS} workers...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Map tasks to futures
        future_to_paper = {executor.submit(download_pdf, pid, url): pid for pid, url in tasks}
        
        if has_tqdm:
            iterator = tqdm(as_completed(future_to_paper), total=total_tasks, desc="Downloading PDFs")
        else:
            iterator = as_completed(future_to_paper)
            
        for i, future in enumerate(iterator):
            paper_id, success, message = future.result()
            
            if success:
                successful += 1
            else:
                failed += 1
                if not has_tqdm:
                    print(f"Failed to download {paper_id}: {message}")
                else:
                    tqdm.write(f"Failed to download {paper_id}: {message}")
                    
            # Basic progress logging for non-tqdm users
            if not has_tqdm and (i + 1) % 100 == 0:
                print(f"Progress: {i + 1}/{total_tasks} (Success: {successful}, Failed: {failed})")

    print(f"\nDownload complete!")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed downloads: {failed}")

if __name__ == "__main__":
    main()
