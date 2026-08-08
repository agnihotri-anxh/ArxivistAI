import json
import sys
from pathlib import Path

# Add backend directory to sys.path so imports work smoothly
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

from app.services.paper_service import upsert_raw_arxiv_paper, upsert_website_paper
from app.db.database import get_raw_arxiv_collection, get_papers_collection

def seed_mongo():
    metadata_path = BACKEND_DIR.parent / "data" / "metadata.json"
    if not metadata_path.exists():
        print(f"Error: {metadata_path} not found!")
        return
        
    print(f"Loading metadata from {metadata_path}...")
    with open(metadata_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"Found {len(data)} paper records in metadata.json.")
    
    count = 0
    for paper_id, record in data.items():
        count += 1
        # Upsert into raw_arxiv_metadata collection
        upsert_raw_arxiv_paper(record)
        # Upsert into papers collection for website catalog
        upsert_website_paper(record)
        
        if count % 100 == 0:
            print(f"Processed {count}/{len(data)} papers...")
            
    raw_coll = get_raw_arxiv_collection()
    papers_coll = get_papers_collection()
    
    print("\n" + "="*50)
    print("MongoDB Atlas Seeding Complete!")
    print(f"  -> raw_arxiv_metadata count: {raw_coll.count_documents({})}")
    print(f"  -> papers (website catalog) count: {papers_coll.count_documents({})}")
    print("="*50)

if __name__ == "__main__":
    seed_mongo()
