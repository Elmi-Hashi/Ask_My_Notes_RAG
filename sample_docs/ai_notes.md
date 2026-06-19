# AI Study Notes

Retrieval-Augmented Generation, also called RAG, is a technique that combines document search with text generation.

A normal language model answers from what it learned during training. A RAG system can answer using extra information from documents provided by the user.

A basic RAG system usually has these steps:

1. Load documents.
2. Split the documents into smaller chunks.
3. Convert the chunks into embeddings.
4. Store the embeddings in a vector database.
5. Convert the user's question into an embedding.
6. Search for the most relevant document chunks.
7. Send the retrieved chunks to a language model.
8. Generate an answer based on the retrieved context.

RAG is useful because it can reduce hallucinations. The model does not need to guess as much because it receives relevant information before answering.

Common tools used in RAG projects include embedding models, vector databases, document loaders, and language models.

Ollama can run language models locally. ChromaDB can store document embeddings locally. Streamlit can be used to build a simple web interface.

A good RAG app should show the sources used for each answer. This makes the system more transparent and helps users trust the result.