"""
RAG 검색 모듈
ChromaDB + BM25 하이브리드 검색
"""

import logging
import chromadb
from rank_bm25 import BM25Okapi
import numpy as np

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, chroma_db_path: str = "./vectordb", collection_name: str = "labor_law"):
        """
        검색 엔진 초기화
        
        Args:
            chroma_db_path: ChromaDB 저장 경로
            collection_name: 컬렉션 이름
        """
        logger.info(f"Initializing ChromaDB from: {chroma_db_path}")
        self.client = chromadb.PersistentClient(path=chroma_db_path)
        self.collection_name = collection_name
        self.collection = None
        self.bm25 = None
        self.bm25_corpus = []
        self.bm25_metadata = []
        
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded collection: {collection_name}")
            # Rebuild BM25 index from existing documents
            self._rebuild_bm25_index()
        except Exception as e:
            logger.info(f"Collection not found, will create on first add: {e}")

    def _rebuild_bm25_index(self):
        """Rebuild BM25 index from ChromaDB documents."""
        if self.collection is None:
            return

        try:
            # Get all documents from collection
            results = self.collection.get()
            if results and results["ids"]:
                doc_ids = results["ids"]
                doc_contents = results["documents"]
                doc_metadatas = results["metadatas"] if results["metadatas"] else [{} for _ in doc_ids]

                # Build BM25 index
                self.bm25_corpus = [doc.split() for doc in doc_contents]
                self.bm25_metadata = [(doc_id, metadata) for doc_id, metadata in zip(doc_ids, doc_metadatas)]
                self.bm25 = BM25Okapi(self.bm25_corpus)

                logger.info(f"Rebuilt BM25 index with {len(doc_ids)} documents")
        except Exception as e:
            logger.warning(f"Failed to rebuild BM25 index: {e}")
    
    def retrieve(self, query_embedding: np.ndarray, top_k: int = 5) -> list:
        """
        벡터 검색
        
        Args:
            query_embedding: 쿼리 임베딩
            top_k: 반환할 결과 수
            
        Returns:
            [{"id": "...", "content": "...", "metadata": {...}, "score": 0.95}, ...]
        """
        if self.collection is None:
            logger.warning("No collection available")
            return []
        
        logger.debug(f"Vector search: top_k={top_k}")
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
        )
        
        retrieved = []
        if results and results["ids"]:
            for idx, doc_id in enumerate(results["ids"][0]):
                retrieved.append({
                    "id": doc_id,
                    "content": results["documents"][0][idx],
                    "metadata": results["metadatas"][0][idx] if results["metadatas"] else {},
                    "score": 1 - results["distances"][0][idx] if results["distances"] else 0,
                })
        
        return retrieved
    
    def hybrid_search(
        self,
        query_embedding: np.ndarray,
        query_text: str,
        top_k: int = 5,
        alpha: float = 0.5,
    ) -> list:
        """
        하이브리드 검색 (벡터 + BM25)
        
        Args:
            query_embedding: 쿼리 임베딩
            query_text: 쿼리 텍스트
            top_k: 반환할 결과 수
            alpha: 벡터 검색 가중치 (1-alpha는 BM25)
            
        Returns:
            통합 검색 결과
        """
        logger.debug(f"Hybrid search: top_k={top_k}, alpha={alpha}")
        
        # 벡터 검색
        vector_results = self.retrieve(query_embedding, top_k)
        
        # BM25 검색
        bm25_results = []
        if self.bm25:
            query_tokens = query_text.split()
            scores = self.bm25.get_scores(query_tokens)
            
            # 상위 top_k 인덱스
            top_indices = np.argsort(scores)[-top_k:][::-1]
            
            for idx in top_indices:
                if scores[idx] > 0:
                    doc_id, metadata = self.bm25_metadata[idx]
                    bm25_results.append({
                        "id": doc_id,
                        "content": " ".join(self.bm25_corpus[idx]),
                        "metadata": metadata,
                        "score": scores[idx],
                    })
        
        # 스코어 통합
        combined = {}
        
        for result in vector_results:
            combined[result["id"]] = alpha * result["score"]
        
        for result in bm25_results:
            if result["id"] in combined:
                combined[result["id"]] += (1 - alpha) * result["score"]
            else:
                combined[result["id"]] = (1 - alpha) * result["score"]
        
        # 정렬 및 결과 반환
        sorted_ids = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        final_results = []
        for doc_id, score in sorted_ids:
            # 메타데이터 포함된 결과 찾기
            for result in vector_results + bm25_results:
                if result["id"] == doc_id:
                    result["score"] = score
                    final_results.append(result)
                    break
        
        return final_results
    
    def add_documents(self, documents: list, embeddings: np.ndarray = None):
        """
        문서 추가
        
        Args:
            documents: [{"id": "...", "content": "...", "metadata": {...}}, ...]
            embeddings: 임베딩 벡터 (없으면 나중에 추가)
        """
        if not documents:
            logger.warning("No documents to add")
            return
        
        logger.info(f"Adding {len(documents)} documents")
        
        # ChromaDB 컬렉션 생성 또는 가져오기
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        
        # 문서 ID, 내용, 임베딩, 메타데이터 준비
        doc_ids = [doc.get("id", str(i)) for i, doc in enumerate(documents)]
        doc_contents = [doc.get("content", "") for doc in documents]
        doc_metadatas = [doc.get("metadata", {}) for doc in documents]
        
        embeddings_list = embeddings.tolist() if embeddings is not None else None
        
        # ChromaDB에 추가
        self.collection.add(
            ids=doc_ids,
            documents=doc_contents,
            embeddings=embeddings_list,
            metadatas=doc_metadatas,
        )
        
        # BM25 인덱스 구축
        self.bm25_corpus = [doc.split() for doc in doc_contents]
        self.bm25_metadata = [(doc_id, metadata) for doc_id, metadata in zip(doc_ids, doc_metadatas)]
        self.bm25 = BM25Okapi(self.bm25_corpus)
        
        logger.info(f"Added {len(documents)} documents successfully")
    
    def clear(self):
        """
        컬렉션 초기화
        """
        logger.info(f"Clearing collection: {self.collection_name}")
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
            self.bm25 = None
            self.bm25_corpus = []
            self.bm25_metadata = []
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
