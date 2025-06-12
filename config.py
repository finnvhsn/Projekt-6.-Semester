import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=f"appdata/.env")

CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "openai_api_base": os.getenv("OPENAI_API_BASE"),
    "openai_embedding_model": os.getenv(
        "OPENAI_EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5"
    ),
    "milvus_uri": os.getenv("MILVUS_URI", "appdata/milvus.db"),
    "milvus_collection": os.getenv("MILVUS_COLLECTION", "knowledge"),
    "judge_threshold": int(os.getenv("JUDGE_THRESHOLD", 7)),
    "max_retries": int(os.getenv("MAX_RETRIES", 3)),
    "llm_model": os.getenv("LLM_MODEL", "gpt-4"),
}
