import os
import traceback
from uuid import uuid4
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from config import CONFIG

# === Load Documents ===
DIRECTORY_PATH = "data/result/markdown"
loader = DirectoryLoader(DIRECTORY_PATH, glob="**/*.md")
raw_docs = loader.load()

# === Split Documents ===
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=350,
    separators=["\n\n", "\n", "."],
)

# === Prepare Chunks ===
docs: list[Document] = []
ids: list[str] = []

for doc in raw_docs:
    chunks = splitter.split_documents([doc])
    file_name = os.path.splitext(
        os.path.basename(doc.metadata.get("source", str(uuid4())))
    )[0]
    for i, chunk in enumerate(chunks):
        chunk.metadata["source_file"] = file_name
        chunk_id = f"{file_name}_{i}"
        docs.append(chunk)
        ids.append(chunk_id)

print(f"📄 Prepared {len(docs)} chunks from {len(raw_docs)} files.")

# === Embedding Model ===
embedding_model = OpenAIEmbeddings(
    model=CONFIG["openai_embedding_model"],
    api_key=CONFIG["openai_api_key"],
    base_url=CONFIG["openai_api_base"],
)

# === FAISS Vector Store ===
try:
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]

    vectorstore = FAISS.from_texts(
        texts=texts, embedding=embedding_model, metadatas=metadatas
    )

    print(f"✅ Stored {len(texts)} chunks in FAISS using file-based IDs.")

    # Optional: persist FAISS index
    faiss_path = "appdata/faiss_index"
    os.makedirs(faiss_path, exist_ok=True)
    vectorstore.save_local(faiss_path)
    print(f"💾 FAISS index saved to {faiss_path}")

except Exception as e:
    traceback.print_exc()
    print(f"❌ Failed to store documents: {e}")
