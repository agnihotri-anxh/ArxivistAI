from pymilvus import MilvusClient
from .config import MILVUS_URI, MILVUS_TOKEN
import os
import hashlib
from collections import Counter
import re
from openai import OpenAI

def get_milvus_client() -> MilvusClient:
    print(f"Connecting to Milvus at {MILVUS_URI}...")
    return MilvusClient(uri=MILVUS_URI, token=MILVUS_TOKEN)

class HybridNvidiaEmbedding:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("NVIDIA_API_KEY", ""),
            base_url="https://integrate.api.nvidia.com/v1"
        )
    
    def encode_queries(self, texts: list[str]):
        # Generate Dense using NVIDIA
        response = self.client.embeddings.create(
            input=texts,
            model="nvidia/nv-embed-v1",
            encoding_format="float",
            extra_body={"input_type": "query", "truncate": "NONE"}
        )
        dense_embs = [item.embedding for item in response.data]
        
        # Generate Sparse using Hashing TF (Stateless, lightweight BM25 alternative)
        sparse_embs = []
        vocab_size = 30000
        for text in texts:
            words = re.findall(r'\w+', text.lower())
            counts = Counter(words)
            sparse_dict = {}
            for word, count in counts.items():
                idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % vocab_size
                # Simple term frequency, can be augmented if needed
                sparse_dict[idx] = sparse_dict.get(idx, 0) + float(count)
            sparse_embs.append(sparse_dict)
            
        return {"dense": dense_embs, "sparse": sparse_embs}

    def encode_documents(self, texts: list[str]):
        # Same as queries for simplicity, but NVIDIA supports "passage" input_type
        response = self.client.embeddings.create(
            input=texts,
            model="nvidia/nv-embed-v1",
            encoding_format="float",
            extra_body={"input_type": "passage", "truncate": "NONE"}
        )
        dense_embs = [item.embedding for item in response.data]
        
        sparse_embs = []
        vocab_size = 30000
        for text in texts:
            words = re.findall(r'\w+', text.lower())
            counts = Counter(words)
            sparse_dict = {}
            for word, count in counts.items():
                idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % vocab_size
                sparse_dict[idx] = sparse_dict.get(idx, 0) + float(count)
            sparse_embs.append(sparse_dict)
            
        return {"dense": dense_embs, "sparse": sparse_embs}

def get_embedding_function():
    use_nvidia = os.getenv("USE_NVIDIA_EMBEDDINGS", "false").lower() == "true"
    nvidia_key = os.getenv("NVIDIA_API_KEY", "").strip()
    if use_nvidia and nvidia_key:
        print("Loading NVIDIA API + Stateless Sparse Encoder...")
        return HybridNvidiaEmbedding()
    else:
        print("Loading BAAI/bge-m3 Hybrid Embedding Model (Local)...")
        from pymilvus.model.hybrid import BGEM3EmbeddingFunction
        return BGEM3EmbeddingFunction(use_fp16=False, device='cpu')


