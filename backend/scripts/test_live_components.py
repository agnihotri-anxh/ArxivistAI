import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env variables
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

sys.path.append(str(BASE_DIR))

def test_all():
    print("=" * 60)
    print("      ARXIVIST AI - SYSTEM & MODEL LIVE HEALTH TEST")
    print("=" * 60)

    # 1. Test MongoDB Atlas
    print("\n[TEST 1/5] Testing MongoDB Atlas Connection...")
    try:
        from pymongo import MongoClient
        mongo_uri = os.getenv("MONGODB_URI")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db_names = client.list_database_names()
        db = client[os.getenv("MONGODB_DB_NAME", "arxivist_ai")]
        coll_names = db.list_collection_names()
        print(f"  -> SUCCESS! Connected to MongoDB Atlas. Collections: {coll_names}")
    except Exception as e:
        print(f"  -> ERROR connecting to MongoDB Atlas: {e}")

    # 2. Test Zilliz / Milvus Cloud Connection
    print("\n[TEST 2/5] Testing Milvus / Zilliz Cloud Connection...")
    try:
        from backend.vector_db.connection import get_milvus_client
        milvus_client = get_milvus_client()
        collections = milvus_client.list_collections()
        print(f"  -> SUCCESS! Connected to Zilliz Cloud. Collections: {collections}")
        
        # Check record count in research_papers collection
        if "research_papers" in collections:
            stats = milvus_client.query(collection_name="research_papers", filter="chunk_index >= 0", limit=1)
            print(f"  -> Successfully queried 'research_papers'. Records exist: {len(stats) > 0}")
    except Exception as e:
        print(f"  -> ERROR connecting to Milvus: {e}")

    # 3. Test Embedding Function
    print("\n[TEST 3/5] Testing Embedding Model Generation...")
    try:
        from backend.vector_db.connection import get_embedding_function
        ef = get_embedding_function()
        sample_text = ["Large Language Models and Retrieval Augmented Generation."]
        res = ef.encode_queries(sample_text)
        dense_dim = len(res["dense"][0]) if "dense" in res else 0
        sparse_len = len(res["sparse"][0]) if hasattr(res["sparse"], "__len__") and not hasattr(res["sparse"], "shape") else "OK"


        print(f"  -> SUCCESS! Dense vector dimensions: {dense_dim}, Sparse tokens generated: {sparse_len}")
    except Exception as e:
        print(f"  -> ERROR in Embedding Model generation: {e}")

    # 4. Test Groq API (Llama 3.3 70B)
    print("\n[TEST 4/5] Testing Groq API (Llama 3.3 70B)...")
    try:
        from openai import OpenAI
        groq_client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Reply with 'Groq Llama-3.3-70B is active'"}],
            max_tokens=20
        )
        msg = response.choices[0].message.content.strip()
        print(f"  -> SUCCESS! Groq Response: '{msg}'")
    except Exception as e:
        print(f"  -> ERROR in Groq API: {e}")

    # 5. Test Full Agentic RAG Pipeline
    print("\n[TEST 5/5] Testing Full Agentic RAG Pipeline...")
    try:
        from backend.app.services.agent import run_agentic_rag
        answer = run_agentic_rag("What are LLMs and RAG?", history=[])
        print(f"  -> SUCCESS! Agent Answer Snippet:\n{answer[:250]}...")
    except Exception as e:
        print(f"  -> ERROR in Agentic RAG Execution: {e}")

    print("\n" + "=" * 60)
    print("      LIVE SYSTEM HEALTH VERIFICATION COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_all()
