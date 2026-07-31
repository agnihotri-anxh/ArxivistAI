from pymilvus import MilvusClient
from pymilvus.model.hybrid import BGEM3EmbeddingFunction
from .config import MILVUS_URI, MODEL_NAME, MILVUS_TOKEN

def get_milvus_client() -> MilvusClient:
    print(f"Connecting to Milvus at {MILVUS_URI}...")
    return MilvusClient(uri=MILVUS_URI, token=MILVUS_TOKEN)

def get_embedding_function() -> BGEM3EmbeddingFunction:
    print(f"Loading BGE-M3 Model ({MODEL_NAME})...")
    return BGEM3EmbeddingFunction(
        model_name=MODEL_NAME,
        device='cpu',  # Change to 'cuda:0' if you have a GPU!
        use_fp16=False
    )
