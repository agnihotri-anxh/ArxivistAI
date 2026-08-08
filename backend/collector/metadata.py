import json
import os
from pathlib import Path
import sys

# Ensure backend modules can be imported if needed
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

class MetadataStore:
    def __init__(self, file_path):
        self.file_path = file_path
        self.records = {}
        self._load()
        
    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                try:
                    self.records = json.load(f)
                except json.JSONDecodeError:
                    self.records = {}
                    
    def save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, indent=2, ensure_ascii=False)
            
    def add_paper(self, paper):
        paper_id = paper.get_short_id()
        data = {
            "id": paper_id,
            "paper_id": paper_id,
            "title": paper.title,
            "summary": paper.summary,
            "authors": [author.name for author in paper.authors],
            "published": paper.published.isoformat(),
            "pdf_url": paper.pdf_url,
            "categories": paper.categories
        }
        self.records[paper_id] = data
        
        # Real-time sync to MongoDB Atlas collections
        try:
            from app.services.paper_service import upsert_raw_arxiv_paper, upsert_website_paper
            upsert_raw_arxiv_paper(data)
            upsert_website_paper(data)
        except Exception as e:
            print(f"[MetadataStore] MongoDB sync note: {e}")
        
    def has_paper(self, paper_id):
        return paper_id in self.records
        
    def get_all(self):
        return list(self.records.values())
