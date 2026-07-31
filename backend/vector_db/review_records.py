import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import vector_db
sys.path.append(str(Path(__file__).resolve().parent.parent))

from vector_db.config import COLLECTION_NAME
from vector_db.connection import get_milvus_client

def main():
    client = get_milvus_client()
    
    print(f"\nQuerying Zilliz Cloud Collection: '{COLLECTION_NAME}'...")
    
    # Query the collection for 2 chunks to see what the data looks like
    res = client.query(
        collection_name=COLLECTION_NAME,
        filter="chunk_index >= 0",  # Simple filter to match records
        limit=2,
        output_fields=["id", "paper_id", "title", "authors", "published_year", "categories", "chunk_index", "contains_image", "text"]
    )
    
    print(f"\nSuccessfully fetched {len(res)} records.\n")
    print("="*50)
    
    for idx, record in enumerate(res):
        print(f"--- RECORD {idx + 1} ---")
        print(f"ID:             {record.get('id')}")
        print(f"Paper ID:       {record.get('paper_id')}")
        print(f"Title:          {record.get('title')}")
        print(f"Authors:        {record.get('authors')}")
        print(f"Year:           {record.get('published_year')}")
        print(f"Categories:     {record.get('categories')}")
        print(f"Chunk Index:    {record.get('chunk_index')}")
        print(f"Contains Image: {record.get('contains_image')}")
        
        # Print a snippet of the text to show the formatting
        text_snippet = record.get('text', '')
        print("\n--- TEXT SNIPPET ---")
        print(text_snippet[:600] + "...\n")
        print("="*50)

if __name__ == "__main__":
    main()
