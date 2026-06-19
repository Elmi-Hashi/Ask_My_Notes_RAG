import os
import hashlib
from typing import List, Dict, Tuple

import requests
import chromadb
from dotenv import load_dotenv
from pypdf import PdfReader


# Load optional settings from .env.
# The app still works without a .env file because we provide defaults below.
load_dotenv()


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemma3:1b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
TOP_K = int(os.getenv("TOP_K", "4"))

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "documents"


def check_ollama_connection() -> bool:
    """
    Check if Ollama is running.

    This is useful because most errors in local RAG projects happen when
    the app is fine, but Ollama is not running in the background.
    """
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def read_file(file_path: str) -> str:
    """
    Read text from a PDF, TXT, or Markdown file.

    PDF text extraction is not always perfect, but it works well enough
    for a small portfolio project like this.
    """
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    if file_path.endswith(".txt") or file_path.endswith(".md"):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    raise ValueError("Unsupported file type. Use PDF, TXT, or Markdown.")


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    """
    Split text into smaller overlapping chunks.

    Made the mistake of not overlapping
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def make_document_id(filename: str, text: str) -> str:
    """
    Create a short stable ID for a document.

    This prevents weird duplicate IDs when the same file is uploaded again.
    """
    raw = f"{filename}-{text[:1000]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def get_embedding(text: str) -> List[float]:
    """
    Create an embedding locally using Ollama.

    Embeddings are just lists of numbers that represent the meaning of text.
    ChromaDB stores these numbers so we can search by similarity.
    """
    response = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": EMBED_MODEL,
            "input": text,
        },
        timeout=120,
    )

    response.raise_for_status()
    data = response.json()

    return data["embeddings"][0]


def get_collection():
    """
    Get or create the local ChromaDB collection.

    ChromaDB saves the vector database in the chroma_db/ folder.
    We ignore that folder in Git because it is generated locally.
    """
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    return chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def ingest_document(file_path: str, filename: str) -> int:
    """
    Read a document, split it into chunks, embed each chunk,
    and store everything in ChromaDB.
    """
    collection = get_collection()

    text = read_file(file_path)

    if not text.strip():
        raise ValueError("The document seems empty or could not be read.")

    chunks = chunk_text(text)
    document_id = make_document_id(filename, text)

    for index, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)

        # Upsert means "insert or update".
        # This is nicer than add() because re-uploading a file will not crash.
        collection.upsert(
            ids=[f"{document_id}-{index}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[
                {
                    "source": filename,
                    "chunk": index,
                    "document_id": document_id,
                }
            ],
        )

    return len(chunks)


def retrieve_context(question: str, top_k: int = TOP_K) -> Tuple[List[str], List[Dict]]:
    """
    Find the document chunks that are most relevant to the user's question.
    """
    collection = get_collection()

    if collection.count() == 0:
        return [], []

    question_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    return documents, metadatas


def build_prompt(question: str, documents: List[str], metadatas: List[Dict]) -> str:
    """
    Build the prompt that gets sent to the local chat model.

    The model is told to only use the retrieved context. This is the
    generation part of RAG.
    """
    context_parts = []

    for index, document in enumerate(documents):
        source = metadatas[index].get("source", "Unknown source")
        chunk = metadatas[index].get("chunk", index)

        context_parts.append(
            f"Source: {source}, chunk {chunk}\n{document}"
        )

    context = "\n\n---\n\n".join(context_parts)

    return f"""
You are a helpful document assistant.

Use only the context below to answer the question.
If the answer is not in the context, say:
"I don't know based on the uploaded documents."

Keep the answer clear and practical.

Context:
{context}

Question:
{question}

Answer:
""".strip()


def generate_answer(prompt: str) -> str:
    """
    Generate an answer using the local Ollama chat model.
    """
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": CHAT_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=300,
    )

    response.raise_for_status()
    data = response.json()

    return data["response"]


def answer_question(question: str) -> Tuple[str, List[Dict]]:
    """
    Full RAG flow:
    1. Embed the question
    2. Retrieve relevant chunks
    3. Send those chunks to the chat model
    4. Return the answer and sources
    """
    documents, metadatas = retrieve_context(question)

    if not documents:
        return (
            "No documents have been ingested yet. Upload and ingest a document first.",
            [],
        )

    prompt = build_prompt(question, documents, metadatas)
    answer = generate_answer(prompt)

    sources = []

    for index, document in enumerate(documents):
        sources.append(
            {
                "source": metadatas[index].get("source", "Unknown source"),
                "chunk": metadatas[index].get("chunk", index),
                "text": document,
            }
        )

    return answer, sources