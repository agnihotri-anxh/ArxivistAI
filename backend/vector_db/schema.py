from pymilvus import MilvusClient, DataType

def setup_collection(client: MilvusClient, collection_name: str) -> str:
    """Creates the Milvus schema and indices if the collection does not exist."""
    if client.has_collection(collection_name):
        return collection_name
        
    print(f"Creating Milvus Collection: {collection_name}...")
    schema = MilvusClient.create_schema(
        auto_id=False,
        enable_dynamic_field=False
    )
    
    schema.add_field(field_name="id", datatype=DataType.VARCHAR, max_length=200, is_primary=True)
    schema.add_field(field_name="paper_id", datatype=DataType.VARCHAR, max_length=100)
    schema.add_field(field_name="title", datatype=DataType.VARCHAR, max_length=2000)
    schema.add_field(field_name="authors", datatype=DataType.VARCHAR, max_length=10000)
    schema.add_field(field_name="published_year", datatype=DataType.INT64)
    schema.add_field(field_name="categories", datatype=DataType.VARCHAR, max_length=500)
    schema.add_field(field_name="chunk_index", datatype=DataType.INT64)
    schema.add_field(field_name="contains_image", datatype=DataType.BOOL)
    schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=60000)
    # Dense Vector for BGE-M3
    schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
    # Sparse Vector for BM25-style keyword matching
    schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
    
    index_params = client.prepare_index_params()
    # Dense Index (Semantic)
    index_params.add_index(
        field_name="dense_vector",
        index_type="AUTOINDEX",
        metric_type="IP"
    )
    # Sparse Index (Keyword)
    index_params.add_index(
        field_name="sparse_vector",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="IP",
        params={"drop_ratio_build": 0.2}
    )
    
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        index_params=index_params
    )
    return collection_name
