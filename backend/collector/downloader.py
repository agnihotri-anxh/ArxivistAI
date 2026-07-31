import os
import yaml
import requests
import concurrent.futures
from tqdm import tqdm
from .metadata import MetadataStore

def load_config(config_path="collector/config.yaml"):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def download_file(url, filepath):
    # Skip if file already exists
    if os.path.exists(filepath):
        return True
        
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Write file with a temporary name first to handle interruptions
        temp_filepath = filepath + ".tmp"
        with open(temp_filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        # Rename once fully downloaded
        os.rename(temp_filepath, filepath)
        return True
    except Exception as e:
        if os.path.exists(filepath + ".tmp"):
            os.remove(filepath + ".tmp")
        return False

def download_papers(max_workers=5):
    config = load_config()
    store = MetadataStore(config["paths"]["metadata"])
    
    pdf_dir = config["paths"]["pdfs"]
    os.makedirs(pdf_dir, exist_ok=True)
    
    papers = store.get_all()
    print(f"Found {len(papers)} papers in metadata database.")
    
    # Filter to only papers we haven't downloaded
    papers_to_download = []
    for paper in papers:
        filepath = os.path.join(pdf_dir, f"{paper['id']}.pdf")
        if not os.path.exists(filepath):
            papers_to_download.append(paper)
            
    print(f"{len(papers) - len(papers_to_download)} already downloaded.")
    print(f"{len(papers_to_download)} left to download.")
    
    if not papers_to_download:
        return
        
    # Download with progress bar and thread pool
    success_count = 0
    fail_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_paper = {
            executor.submit(download_file, paper['pdf_url'], os.path.join(pdf_dir, f"{paper['id']}.pdf")): paper 
            for paper in papers_to_download
        }
        
        # Process results with tqdm progress bar
        for future in tqdm(concurrent.futures.as_completed(future_to_paper), total=len(papers_to_download), desc="Downloading PDFs"):
            paper = future_to_paper[future]
            try:
                success = future.result()
                if success:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                fail_count += 1
                
    print(f"\nDownload complete! Success: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    download_papers()
