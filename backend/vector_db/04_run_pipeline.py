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

def main():
    client = get_milvus_client()
    collection_name = setup_collection(client, COLLECTION_NAME)
    
    bge_m3_ef = get_embedding_function()
    markdown_splitter, recursive_splitter = get_splitters()
    
    print("Loading metadata.json...")
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        master_metadata = json.load(f)
        
    json_files = list(JSON_DIR.glob("*.json"))
    print(f"Found {len(json_files)} extracted JSON files to index.")
    
    for json_file in json_files:
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
        try:
            published_year = int(published[:4]) if published else 0
        except ValueError:
            published_year = 0
            
        full_text = paper_data.get("full_text", "")
        
        clean_text, conclusion_text = extract_conclusion_and_strip_references(full_text)
        
        md_header_splits = markdown_splitter.split_text(clean_text)
        chunks = recursive_splitter.split_documents(md_header_splits)
        
        if not chunks:
            print(f"Warning: No text chunks found for {paper_id}")
            continue
            
        enhanced_context = f"# {title}\n\n**Abstract:** {summary}\n\n"
        if conclusion_text:
            enhanced_context += f"**Key Findings (Conclusion):** {conclusion_text[:1500]}...\n\n"
        chunks[0].page_content = enhanced_context + chunks[0].page_content
        
        data_to_insert = []
        chunk_texts_for_embedding = []
        
        for idx, doc in enumerate(chunks):
            chunk_str = doc.page_content
            header_context = " > ".join(doc.metadata.values()) if doc.metadata else ""
            if header_context:
                chunk_str = f"[{header_context}]\n{chunk_str}"
                
            chunk_str = chunk_str[:59000]
            contains_image = bool(re.search(r"\[FIGURE_.*_INSERT_HERE:", chunk_str))
            
            chunk_texts_for_embedding.append(chunk_str)
            
            data_to_insert.append({
                "id": f"{paper_id}_{idx}",
                "paper_id": paper_id,
                "title": title[:1999],
                "authors": authors,
                "published_year": published_year,
                "categories": categories,
                "chunk_index": idx,
                "contains_image": contains_image,
                "text": chunk_str
            })
            
        print(f"  -> Generating Hybrid Embeddings for {len(chunk_texts_for_embedding)} chunks...")
        embeddings = bge_m3_ef.encode_documents(chunk_texts_for_embedding)
        
        dense_vectors = embeddings["dense"]
        sparse_vectors = embeddings["sparse"]
        
        for i in range(len(data_to_insert)):
            data_to_insert[i]["dense_vector"] = dense_vectors[i]
            # Convert SciPy matrix row to dictionary for Milvus insertion
            sparse_row = sparse_vectors[i]
            if hasattr(sparse_row, 'coords') and hasattr(sparse_row, 'data'):
                # Handle scipy coo_array
                data_to_insert[i]["sparse_vector"] = {int(k): float(v) for k, v in zip(sparse_row.coords[0], sparse_row.data)}
            elif hasattr(sparse_row, 'indices') and hasattr(sparse_row, 'data'):
                # Handle scipy csr_array
                data_to_insert[i]["sparse_vector"] = {int(k): float(v) for k, v in zip(sparse_row.indices, sparse_row.data)}
            elif isinstance(sparse_row, dict):
                data_to_insert[i]["sparse_vector"] = sparse_row
            else:
                # Fallback if it's some other format
                data_to_insert[i]["sparse_vector"] = sparse_row
            
        client.insert(collection_name=collection_name, data=data_to_insert)
        print(f"  -> Inserted {len(data_to_insert)} chunks into Milvus for {paper_id}")
        
    print("\nVector Database Construction Complete!")

if __name__ == "__main__":
    main()
