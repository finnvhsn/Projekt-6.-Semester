# 🧠 Document-based Chat System

This project enables question-answering over your document collection using a vector database and a local LLM or API-backed model.

---

## 🚀 Quick Start

### 1. Configure your .env
Create a `.env` file in the `appdata/` directory with your API keys and database configurations. You can copy the example from `.env.example`.

```bash
cp .env_example appdata/.env
```

### 2. Install Dependencies
Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Preprocess Your Documents

Convert your documents into a machine-readable format:

```
python preprocess.py --ext .docx .pdf
```

You can specify one or more supported file extensions with the `--ext` flag.

---

### 4. Build the Vector Index

Generate embeddings and load them into your vector database:

```
python build_vector.py
```

Make sure your vector DB (e.g., Milvus, FAISS) is properly configured before running this step.

---

### 5. Start Chatting with Your Data

Ask questions based on the ingested documents:

```
python main.py "What is the summary of the contract?"
```

Replace the example question with your own.

---

## 📁 Folder Structure

```
.
├── data/input          # Input documents
├── result/markdown/    # Preprocessed markdown outputs
├── preprocess.py       # Converts files to markdown
├── build_vector.py     # Embeds and stores vectors
└── main.py             # QA interface entrypoint
```

---

## 🔧 Configuration

Make sure to update or review your config files (e.g., `config.py`, `appdata/.env`) for paths, vector DB credentials, and model API keys.

---

## ✅ Supported Extensions

- `.docx`
- `.pdf`
- (and more, see [docling documentation](https://github.com/docling-project/docling) for full list)

---

## 📌 Requirements

- Python 3.10+
- Dependencies in `requirements.txt`  
  *(install via `pip install -r requirements.txt`)*
- Vector database Milvus
- LLM backend (OpenAI API compatible)

---

## 💬 Example Use Case

Upload internal documents, process them, and ask questions like:

> "What are the main obligations in the NDA?"

This enables semantic search and natural language interaction with your documents.
