# Ask My Notes

Ask My Notes is a local Retrieval-Augmented Generation app that lets users upload documents and ask questions about them.

It uses Ollama for the local language model, ChromaDB for vector storage, and Streamlit for the web interface.

## Features

- Upload PDF, TXT, or Markdown files
- Split documents into searchable chunks
- Create local embeddings with Ollama
- Store vectors in ChromaDB
- Ask questions in a chat interface
- Generate answers using retrieved document context
- Show source snippets used for each answer
- No OpenAI API key required

## Important Note About Models

This repository does not include any model files.

To keep the repo lightweight, users must install Ollama and pull their own models.

Recommended models:

```bash
ollama pull gemma3:1b
ollama pull nomic-embed-text
```

The default setup uses:

```txt
CHAT_MODEL=gemma3:1b
EMBED_MODEL=nomic-embed-text
```

You can change these in a `.env` file.

## Tech Stack

- Python
- Streamlit
- Ollama
- ChromaDB
- pypdf
- requests

## How It Works

1. A user uploads a document.
2. The app extracts the text.
3. The text is split into overlapping chunks.
4. Ollama creates embeddings for each chunk.
5. ChromaDB stores the chunks and embeddings.
6. When the user asks a question, the app retrieves the most relevant chunks.
7. The retrieved chunks are sent to the local chat model.
8. The model generates an answer using the document context.

## Setup

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/ask-my-notes.git
cd ask-my-notes
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Install Ollama Models

Install Ollama first.

Then pull the recommended models:

```bash
ollama pull gemma3:1b
ollama pull nomic-embed-text
```

## Optional Environment File

Create a `.env` file if you want to change the default settings:

```txt
OLLAMA_URL=http://localhost:11434
CHAT_MODEL=gemma3:1b
EMBED_MODEL=nomic-embed-text
TOP_K=4
```

If you do not create a `.env` file, the app will use these default values automatically.

## Run the App

```bash
streamlit run app.py
```

Then open the local Streamlit URL in your browser.

## Example Questions

After uploading a document, try asking:

- What is this document about?
- Summarize the main points.
- What are the key takeaways?
- What does the document say about RAG?
- Explain this document in simple terms.

## Project Structure

```txt
ask-my-notes/
├── app.py
├── rag.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── sample_docs/
    └── ai_notes.md
```

## Why This Project Exists

This project is meant to be a beginner-friendly RAG app that runs locally.

It avoids paid APIs and keeps the GitHub repository lightweight by not including model files, uploaded documents, or generated vector databases.

Users bring their own local Ollama models.

## What I Learned

- How Retrieval-Augmented Generation works
- How to chunk documents
- How embeddings are used for semantic search
- How to store vectors in ChromaDB
- How to connect a local LLM to a Streamlit app
- How to keep model files and local data out of GitHub

## Notes

The generated answers depend on the model you use.

Smaller models are faster, but larger models may give better answers.