from typing import List, Dict, Optional, Any
from datetime import datetime
from ..db.database import get_raw_arxiv_collection, get_papers_collection
from .category_utils import format_category_name

def get_website_papers(
    category: Optional[str] = None,
    year: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 24
) -> Dict[str, Any]:
    """Fetches paginated papers from the MongoDB website catalog collection."""
    papers_coll = get_papers_collection()
    query = {}
    
    if category and category != "All":
        query["category"] = category
    if year and year != "All":
        query["year"] = str(year)
    if search and search.strip():
        regex_pattern = f".*{search.strip()}.*"
        query["$or"] = [
            {"title": {"$regex": regex_pattern, "$options": "i"}},
            {"full_abstract": {"$regex": regex_pattern, "$options": "i"}},
            {"authors": {"$regex": regex_pattern, "$options": "i"}}
        ]
        
    total = papers_coll.count_documents(query)
    total_pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
    skip = (max(1, page) - 1) * limit
    
    cursor = papers_coll.find(query, {"_id": 0}).skip(skip).limit(limit)
    papers = list(cursor)
    
    return {
        "papers": papers,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }

def get_paper_by_id(paper_id: str) -> Optional[Dict]:
    """Fetches a single paper by its arXiv paper_id."""
    papers_coll = get_papers_collection()
    return papers_coll.find_one({"paper_id": paper_id}, {"_id": 0})

def upsert_raw_arxiv_paper(data: Dict):
    """Upserts a raw arXiv paper metadata document into raw_arxiv_metadata collection."""
    raw_coll = get_raw_arxiv_collection()
    paper_id = data.get("paper_id") or data.get("id")
    if not paper_id:
        return
        
    doc = {
        "paper_id": paper_id,
        "title": data.get("title", ""),
        "authors": data.get("authors", []),
        "categories": data.get("categories", []),
        "summary": data.get("summary", "") or data.get("abstract", ""),
        "published": data.get("published", ""),
        "pdf_url": data.get("pdf_url", f"/api/pdfs/{paper_id}.pdf"),
        "embedding_status": data.get("embedding_status", "pending"),
        "harvested_at": datetime.utcnow()
    }
    raw_coll.update_one({"paper_id": paper_id}, {"$set": doc}, upsert=True)

def upsert_website_paper(data: Dict):
    """Upserts a clean paper record into the website catalog papers collection."""
    papers_coll = get_papers_collection()
    paper_id = data.get("paper_id") or data.get("id")
    if not paper_id:
        return
        
    raw_categories = data.get("categories", [])
    if isinstance(raw_categories, list):
        primary_raw = raw_categories[0] if raw_categories else "Research"
    else:
        primary_raw = str(raw_categories).split(",")[0].strip() if raw_categories else "Research"
        
    readable_cat = format_category_name(primary_raw)
    
    published = str(data.get("published", ""))
    year = str(data.get("published_year", "")) if data.get("published_year") else (published[:4] if len(published) >= 4 else "2024")
    
    authors = data.get("authors", [])
    if isinstance(authors, str):
        authors = [a.strip() for a in authors.split(",") if a.strip()]
        
    doc = {
        "id": paper_id,
        "paper_id": paper_id,
        "title": data.get("title", f"Document {paper_id}"),
        "authors": authors,
        "category": readable_cat,
        "raw_category": primary_raw,
        "year": year,
        "published": published,
        "abstract": (data.get("summary") or data.get("abstract", ""))[:300] + "...",
        "full_abstract": data.get("summary") or data.get("abstract", ""),
        "pdf_url": f"/api/pdfs/{paper_id}.pdf",
        "tags": [],
        "venue": "ArXiv",
        "created_at": datetime.utcnow()
    }
    papers_coll.update_one({"paper_id": paper_id}, {"$set": doc}, upsert=True)
