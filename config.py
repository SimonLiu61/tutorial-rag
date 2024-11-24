# config.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any

class RAGConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """RAG 系统配置"""
    openai_api_key: str
    chunk_size: int = 800
    chunk_overlap: int = 150
    model_name: str = "gpt-4-turbo-preview"
    temperature: float = 0.1
    embedding_model: str = "text-embedding-3-small"
    top_k: int = 5
    max_tokens: int = 3000
    data_dir: str = "data"
    persist_directory: str = "./chroma_db"