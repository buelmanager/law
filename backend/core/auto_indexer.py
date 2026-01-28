"""
Auto-indexer for labor law documents.
Called on startup if ChromaDB collection is empty.
"""

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

# Path to pre-collected labor laws data
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "collect" / "labor_laws.jsonl"
VECTORDB_PATH = Path(__file__).parent.parent.parent / "vectordb"


def auto_index_labor_laws(retriever, embeddings_mgr, force_recreate=True):
    """
    Automatically index labor law documents if collection is empty.

    Args:
        retriever: Retriever instance
        embeddings_mgr: EmbeddingsManager instance
        force_recreate: If True, delete and recreate vectordb on version mismatch
    """
    if embeddings_mgr is None:
        logger.warning("EmbeddingsManager not available, skipping auto-indexing")
        return

    if not DATA_PATH.exists():
        logger.warning(f"Data file not found: {DATA_PATH}")
        return

    # If force_recreate, delete old vectordb to avoid version conflicts
    if force_recreate and VECTORDB_PATH.exists():
        logger.info(f"Removing old vectordb at {VECTORDB_PATH} due to version mismatch...")
        try:
            shutil.rmtree(VECTORDB_PATH)
            VECTORDB_PATH.mkdir(parents=True, exist_ok=True)
            logger.info("Old vectordb removed, creating fresh database...")

            # Reinitialize retriever with fresh database
            import chromadb
            retriever.client = chromadb.PersistentClient(path=str(VECTORDB_PATH))
            retriever.collection = None
        except Exception as e:
            logger.error(f"Failed to remove old vectordb: {e}")

    logger.info(f"Loading documents from {DATA_PATH}")

    try:
        import json

        # Load documents from JSONL
        raw_docs = []
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    raw_docs.append(json.loads(line))

        if not raw_docs:
            logger.warning("No documents found in data file")
            return

        logger.info(f"Loaded {len(raw_docs)} raw documents")

        # Simple chunking - use document content directly for now
        docs_for_retriever = []
        chunk_contents = []

        for i, doc in enumerate(raw_docs):
            doc_id = doc.get("id", f"doc_{i}")
            content = doc.get("content", "")
            law_name = doc.get("law", doc_id)

            if not content:
                content = f"법령: {law_name}"

            # For simplicity, treat each document as a single chunk
            # In production, you'd want proper chunking
            docs_for_retriever.append({
                "id": f"chunk_{i}",
                "content": content[:2000],  # Limit content size
                "metadata": {
                    "law": law_name,
                    "type": doc.get("type", "law"),
                }
            })
            chunk_contents.append(content[:2000])

        logger.info(f"Prepared {len(docs_for_retriever)} documents for indexing")

        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = embeddings_mgr.encode_batch(chunk_contents)
        logger.info(f"Generated embeddings shape: {embeddings.shape}")

        # Add to retriever
        logger.info("Adding documents to ChromaDB...")
        retriever.add_documents(docs_for_retriever, embeddings=embeddings)
        logger.info(f"Successfully indexed {len(docs_for_retriever)} documents")

    except Exception as e:
        logger.error(f"Auto-indexing error: {e}")
        raise
