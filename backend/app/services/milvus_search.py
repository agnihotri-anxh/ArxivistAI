import sys
from pathlib import Path
from typing import List, Dict
from pymilvus import AnnSearchRequest, RRFRanker
from ..core.config import settings

# We need to import our vector_db package from the parent directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from backend.vector_db.connection import get_milvus_client, get_embedding_function
from backend.vector_db.config import COLLECTION_NAME
from .category_utils import format_category_name

# Initialize connections lazily or globally
client = None
embedding_fn = None

def init_milvus():
    global client, embedding_fn
    if client is None:
        client = get_milvus_client()
    if embedding_fn is None:
        embedding_fn = get_embedding_function()

def get_all_papers(limit: int = 500) -> List[Dict]:
    """Fetches a list of unique papers from the database."""
    client = get_milvus_client()
    
    # By filtering for chunk_index == 0, we get exactly one record per paper
    res = client.query(
        collection_name=COLLECTION_NAME,
        filter="chunk_index == 0",
        output_fields=["paper_id", "title", "authors", "published_year", "categories", "text"],
        limit=limit
    )
    
    papers = []
    for r in res:
        raw_cat = r.get("categories", "").split(",")[0].strip() if r.get("categories") else "Research"
        readable_cat = format_category_name(raw_cat)
        papers.append({
            "id": r.get("paper_id", ""),
            "title": r.get("title", ""),
            "authors": [a.strip() for a in r.get("authors", "").split(",")],
            "category": readable_cat,
            "raw_category": raw_cat,
            "year": str(r.get("published_year", "")),
            "abstract": r.get("text", "")[:300] + "...",
            "tags": [],
            "venue": "ArXiv"
        })
    return papers

def search_academic_database(query: str, limit: int = 5) -> List[Dict]:
    """Performs a hybrid search on Zilliz Cloud."""
    init_milvus()
    
    # Generate query embeddings
    print(f"Embedding query: '{query}'")
    embeddings = embedding_fn.encode_queries([query])
    
    dense_vec = embeddings["dense"][0]
    sparse_vec = embeddings["sparse"][0]
    
    # Convert sparse query vector to dict
    if hasattr(sparse_vec, 'coords'):
        sparse_dict = {int(k): float(v) for k, v in zip(sparse_vec.coords[0], sparse_vec.data)}
    elif hasattr(sparse_vec, 'indices'):
        sparse_dict = {int(k): float(v) for k, v in zip(sparse_vec.indices, sparse_vec.data)}
    else:
        sparse_dict = sparse_vec
        
    # Define the Dense Search Request
    dense_req = AnnSearchRequest(
        data=[dense_vec],
        anns_field="dense_vector",
        param={"metric_type": "IP"},
        limit=limit
    )
    
    # Define the Sparse Search Request
    sparse_req = AnnSearchRequest(
        data=[sparse_dict],
        anns_field="sparse_vector",
        param={"metric_type": "IP"},
        limit=limit
    )
    
    # Perform Hybrid Search using Reciprocal Rank Fusion
    res = client.hybrid_search(
        collection_name=COLLECTION_NAME,
        reqs=[dense_req, sparse_req],
        ranker=RRFRanker(),
        limit=limit,
        output_fields=["title", "authors", "published_year", "text"]
    )
    
    # Format the results
    formatted_results = []
    for hit in res[0]:
        doc = hit.entity
        formatted_results.append({
            "title": doc.get("title"),
            "authors": doc.get("authors"),
            "published_year": doc.get("published_year"),
            "text": doc.get("text"),
            "distance": hit.distance
        })
        
    return formatted_results
