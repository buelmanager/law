"""Pipeline to process, chunk, embed, and index collected law documents.

Usage:
    python data/process/index_labor_laws.py

This script:
1. Loads raw documents from data/collect/labor_laws.jsonl
2. Chunks them using DocumentChunker (by article or text size)
3. Generates embeddings using EmbeddingsManager
4. Stores in ChromaDB via Retriever.add_documents
"""

import sys
import os
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import logging
from data.collect import load_documents
from data.process import DocumentChunker, clean_text, extract_metadata
from backend.core.embeddings import EmbeddingsManager
from backend.core.retriever import Retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

INPUT_PATH = Path(__file__).parent.parent / "collect" / "labor_laws.jsonl"
VECTORDB_PATH = Path(__file__).parent.parent.parent / "vectordb"


def main():
    logger.info("Starting data indexing pipeline...")
    
    # 1. Load documents
    logger.info(f"Loading documents from {INPUT_PATH}")
    raw_docs = load_documents(str(INPUT_PATH))
    if not raw_docs:
        logger.warning("No documents loaded")
        return
    logger.info(f"Loaded {len(raw_docs)} raw documents")
    
    # 2. Initialize chunker, embeddings, and retriever
    chunker = DocumentChunker(chunk_size=512, overlap=100)
    embeddings_mgr = EmbeddingsManager(model_name="intfloat/multilingual-e5-large")
    retriever = Retriever(chroma_db_path=str(VECTORDB_PATH), collection_name="labor_law")
    
    # 3. Process documents: clean → chunk → extract metadata
    logger.info("Chunking documents...")
    all_chunks = []
    for i, doc in enumerate(raw_docs):
        doc_id = doc.get("id", f"doc_{i}")
        content = doc.get("content", "")
        
        # Clean text
        if content:
            content = clean_text(content)
        
        # If no content, store minimal record
        if not content:
            content = f"법령: {doc.get('law', doc_id)}"
        
        # Chunk by articles if present; otherwise by text size
        metadata = extract_metadata(doc)
        chunks = chunker.chunk_by_law_articles(content, law_name=metadata.get("law", ""))
        
        if not chunks:
            # Fallback: chunk by size
            chunks = chunker.chunk_text(content, metadata=metadata)
        
        all_chunks.extend(chunks)
    
    logger.info(f"Created {len(all_chunks)} chunks")
    
    # 4. Generate embeddings
    logger.info("Generating embeddings...")
    chunk_contents = [c["content"] for c in all_chunks]
    embeddings = embeddings_mgr.encode_batch(chunk_contents)
    logger.info(f"Generated embeddings shape: {embeddings.shape}")
    
    # 5. Prepare documents for retriever
    docs_for_retriever = []
    for i, chunk in enumerate(all_chunks):
        docs_for_retriever.append({
            "id": f"chunk_{i}",
            "content": chunk["content"],
            "metadata": {
                "law": chunk.get("law", ""),
                "article": chunk.get("article", ""),
                "type": chunk.get("type", ""),
            }
        })
    
    # 6. Add to retriever (ChromaDB)
    logger.info("Indexing documents in ChromaDB...")
    retriever.add_documents(docs_for_retriever, embeddings=embeddings)
    logger.info(f"Indexed {len(docs_for_retriever)} documents in ChromaDB")
    logger.info(f"ChromaDB path: {VECTORDB_PATH}")
    
    logger.info("✅ Indexing pipeline complete!")


if __name__ == "__main__":
    main()
