import json
import re
import sys
from pathlib import Path

# Add the parent directory to the path so we can import vector_db
sys.path.append(str(Path(__file__).resolve().parent.parent))

from vector_db.config import METADATA_PATH, JSON_DIR, COLLECTION_NAME
from vector_db.connection import get_milvus_client, get_embedding_function
from vector_db.schema import setup_collection
from vector_db.chunking import get_splitters, extract_conclusion_and_strip_references

def main(max_records=None):
    client = get_milvus_client()
    collection_name = setup_collection(client, COLLECTION_NAME)
    
    bge_m3_ef = get_embedding_function()
    markdown_splitter, recursive_splitter = get_splitters()
    
    print("Loading metadata.json...")
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        master_metadata = json.load(f)
        
    json_files = list(JSON_DIR.glob("*.json"))
    print(f"Found {len(json_files)} extracted JSON files to index.")
    
    indexed_count = 0
    for json_file in json_files:
        if max_records is not None and indexed_count >= max_records:
            print(f"Reached batch limit of {max_records} vector embedding documents.")
            break
            
        with open(json_file, "r", encoding="utf-8") as f:
            paper_data = json.load(f)
            
        paper_id = paper_data["metadata"]["paper_id"]
        
        # Check idempotency
        res = client.query(
            collection_name=collection_name,
            filter=f"paper_id == '{paper_id}'",
            limit=1
        )
        if res:
            print(f"Skipping {paper_id} - Already embedded in Milvus!")
            continue
            
        print(f"Processing {paper_id}...")
        
        rich_meta = master_metadata.get(paper_id, {})
        title = rich_meta.get("title", f"Document {paper_id}")
        authors = ", ".join(rich_meta.get("authors", []))[:9999]
        summary = rich_meta.get("summary", "")
        categories = ", ".join(rich_meta.get("categories", []))[:499]
        published = rich_meta.get("published", "")
        pdf_url = rich_meta.get("pdf_url", "")
        
        full_text = paper_data.get("full_text", "")
        cleaned_text, conclusion_text = extract_conclusion_and_strip_references(full_text)
        
        md_docs = markdown_splitter.create_documents([cleaned_text])
        
        final_chunks = []
        for doc in md_docs:
            if len(doc.page_content) > 1000:
                sub_docs = recursive_splitter.create_documents([doc.page_content])
                final_chunks.extend(sub_docs)
            else:
                final_chunks.append(doc)
                
        chunks_data = []
        
        # 1. Title chunk (chunk 0)
        chunks_data.append({
            "paper_id": paper_id,
            "chunk_index": 0,
            "text": f"Title: {title}\nSummary: {summary}",
            "section": "Header",
            "title": title,
            "authors": authors,
            "categories": categories,
            "published": published,
            "pdf_url": pdf_url
        })
        
        # 2. Main content chunks
        for idx, chunk in enumerate(final_chunks, start=1):
            chunks_data.append({
                "paper_id": paper_id,
                "chunk_index": idx,
                "text": chunk.page_content,
                "section": "Body",
                "title": title,
                "authors": authors,
                "categories": categories,
                "published": published,
                "pdf_url": pdf_url
            })
            
        # 3. Conclusion chunk
        if conclusion_text:
            chunks_data.append({
                "paper_id": paper_id,
                "chunk_index": len(final_chunks) + 1,
                "text": f"Conclusion:\n{conclusion_text}",
                "section": "Conclusion",
                "title": title,
                "authors": authors,
                "categories": categories,
                "published": published,
                "pdf_url": pdf_url
            })
            
        # Generate BGE-M3 Embeddings
        texts = [c["text"] for c in chunks_data]
        embeddings = bge_m3_ef(texts)
        
        dense_vectors = embeddings["dense"]
        sparse_vectors = embeddings["sparse"]
        
        rows = []
        for i, c in enumerate(chunks_data):
            rows.append({
                "paper_id": c["paper_id"],
                "chunk_index": c["chunk_index"],
                "text": c["text"],
                "section": c["section"],
                "title": c["title"],
                "authors": c["authors"],
                "categories": c["categories"],
                "published": c["published"],
                "pdf_url": c["pdf_url"],
                "vector": dense_vectors[i],
                "sparse_vector": sparse_vectors[i]
            })
            
        client.insert(collection_name=collection_name, data=rows)
        print(f"Successfully inserted {len(rows)} chunks into Milvus for {paper_id}")
        indexed_count += 1
        
    print(f"\nPhase 4 (Milvus Ingestion) Complete! Indexed {indexed_count} documents.")

if __name__ == "__main__":
    main()
