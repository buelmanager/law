"""
판례/해석례 데이터를 ChromaDB에 인덱싱하는 파이프라인

사용법:
    python index_cases.py --input data/raw/categories --collection law_cases
    python index_cases.py --category labor
"""

import os
import sys
import json
import logging
import argparse
import requests
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# 프로젝트 루트 추가
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import chromadb
from chromadb.config import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@dataclass
class CaseChunk:
    """인덱싱할 청크 단위"""
    id: str
    text: str
    metadata: Dict[str, Any]


class CaseIndexer:
    """판례/해석례 인덱싱 파이프라인"""

    def __init__(
        self,
        chroma_path: str = None,
        collection_name: str = "law_cases",
        embeddings_model: str = "intfloat/multilingual-e5-small"
    ):
        self.chroma_path = Path(chroma_path) if chroma_path else PROJECT_ROOT / "vectordb"
        self.chroma_path.mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name
        self.embeddings_model = embeddings_model
        self.model = None
        self.client = None
        self.collection = None

    def _init_embeddings(self):
        """로컬 임베딩 모델 초기화"""
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"🔄 임베딩 모델 로드: {self.embeddings_model}")
            self.model = SentenceTransformer(self.embeddings_model)
            logger.info("✅ 임베딩 모델 로드 완료")

    def _encode_batch(self, texts: List[str]) -> List[List[float]]:
        """배치 임베딩 생성 (로컬 모델)"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def _init_chroma(self):
        """ChromaDB 초기화"""
        if self.client is None:
            logger.info(f"🔄 ChromaDB 초기화: {self.chroma_path}")
            self.client = chromadb.PersistentClient(
                path=str(self.chroma_path),
                settings=Settings(anonymized_telemetry=False)
            )
            # 기존 컬렉션이 있으면 삭제 후 재생성 (clean index)
            try:
                self.client.delete_collection(self.collection_name)
                logger.info(f"🗑️ 기존 컬렉션 삭제: {self.collection_name}")
            except Exception:
                pass

            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"✅ 컬렉션 생성: {self.collection_name}")

    def load_jsonl(self, filepath: Path) -> List[Dict[str, Any]]:
        """JSONL 파일 로드"""
        items = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    items.append(json.loads(line))
        logger.info(f"📂 로드: {filepath.name} ({len(items)}건)")
        return items

    def chunk_precedent(self, prec: Dict[str, Any]) -> List[CaseChunk]:
        """
        판례를 청크로 분할

        청킹 전략:
        1. 판시사항 (summary) - 핵심 법리
        2. 판결요지 (holding) - 결론
        3. 전문 (full_text) - 상세 내용 (너무 길면 분할)
        """
        chunks = []
        case_number = prec.get("case_number", "")
        base_id = prec.get("id", "")
        category = prec.get("category", "unknown")

        # 공통 메타데이터
        base_meta = {
            "type": "precedent",
            "category": category,
            "case_number": case_number,
            "title": prec.get("title", ""),
            "date": prec.get("date", ""),
            "court": prec.get("court", ""),
            "case_type": prec.get("case_type", ""),
            "source": f"판례 {case_number}",
        }

        # 1. 판시사항
        summary = prec.get("summary", "").strip()
        if summary and len(summary) > 50:
            chunks.append(CaseChunk(
                id=f"prec_{base_id}_summary",
                text=f"[판시사항] {summary}",
                metadata={**base_meta, "chunk_type": "summary"}
            ))

        # 2. 판결요지
        holding = prec.get("holding", "").strip()
        if holding and len(holding) > 50:
            chunks.append(CaseChunk(
                id=f"prec_{base_id}_holding",
                text=f"[판결요지] {holding}",
                metadata={**base_meta, "chunk_type": "holding"}
            ))

        # 3. 전문 (길면 분할)
        full_text = prec.get("full_text", "").strip()
        if full_text and len(full_text) > 100:
            # 2000자 단위로 분할
            max_len = 2000
            if len(full_text) <= max_len:
                chunks.append(CaseChunk(
                    id=f"prec_{base_id}_full",
                    text=f"[판례 전문] {full_text}",
                    metadata={**base_meta, "chunk_type": "full_text"}
                ))
            else:
                for i in range(0, len(full_text), max_len):
                    chunk_text = full_text[i:i + max_len]
                    chunks.append(CaseChunk(
                        id=f"prec_{base_id}_full_{i // max_len}",
                        text=f"[판례 전문 Part {i // max_len + 1}] {chunk_text}",
                        metadata={**base_meta, "chunk_type": f"full_text_part_{i // max_len}"}
                    ))

        return chunks

    def chunk_interpretation(self, expc: Dict[str, Any]) -> List[CaseChunk]:
        """
        법령해석례를 청크로 분할

        청킹 전략:
        1. 질의요지 (question) - 질문 내용
        2. 회답 (answer) - 답변
        3. 이유 (reason) - 상세 이유
        """
        chunks = []
        case_number = expc.get("case_number", "")
        base_id = expc.get("id", "")
        category = expc.get("category", "unknown")

        # 공통 메타데이터
        base_meta = {
            "type": "interpretation",
            "category": category,
            "case_number": case_number,
            "title": expc.get("title", ""),
            "date": expc.get("date", ""),
            "requester": expc.get("requester", ""),
            "responder": expc.get("responder", ""),
            "source": f"법령해석례 {case_number}",
        }

        # 1. 질의요지
        question = expc.get("question", "").strip()
        if question and len(question) > 30:
            chunks.append(CaseChunk(
                id=f"expc_{base_id}_question",
                text=f"[질의요지] {question}",
                metadata={**base_meta, "chunk_type": "question"}
            ))

        # 2. 회답
        answer = expc.get("answer", "").strip()
        if answer and len(answer) > 30:
            chunks.append(CaseChunk(
                id=f"expc_{base_id}_answer",
                text=f"[회답] {answer}",
                metadata={**base_meta, "chunk_type": "answer"}
            ))

        # 3. 이유
        reason = expc.get("reason", "").strip()
        if reason and len(reason) > 50:
            # 이유가 길면 분할
            max_len = 2000
            if len(reason) <= max_len:
                chunks.append(CaseChunk(
                    id=f"expc_{base_id}_reason",
                    text=f"[이유] {reason}",
                    metadata={**base_meta, "chunk_type": "reason"}
                ))
            else:
                for i in range(0, len(reason), max_len):
                    chunk_text = reason[i:i + max_len]
                    chunks.append(CaseChunk(
                        id=f"expc_{base_id}_reason_{i // max_len}",
                        text=f"[이유 Part {i // max_len + 1}] {chunk_text}",
                        metadata={**base_meta, "chunk_type": f"reason_part_{i // max_len}"}
                    ))

        return chunks

    def index_files(
        self,
        input_dir: Path,
        category_filter: Optional[str] = None,
        batch_size: int = 100
    ) -> Dict[str, int]:
        """
        디렉토리 내 모든 JSONL 파일 인덱싱

        Args:
            input_dir: 입력 디렉토리
            category_filter: 특정 카테고리만 필터 (예: "labor")
            batch_size: 배치 사이즈

        Returns:
            인덱싱 통계
        """
        self._init_embeddings()
        self._init_chroma()

        all_chunks: List[CaseChunk] = []
        stats = {"precedents": 0, "interpretations": 0, "chunks": 0}

        # JSONL 파일 찾기
        jsonl_files = list(input_dir.glob("*.jsonl"))
        if category_filter:
            jsonl_files = [f for f in jsonl_files if f.name.startswith(category_filter)]

        logger.info(f"\n📁 입력 디렉토리: {input_dir}")
        logger.info(f"📄 JSONL 파일: {len(jsonl_files)}개")

        for filepath in jsonl_files:
            items = self.load_jsonl(filepath)

            # 파일명에서 타입 추론
            if "precedent" in filepath.name:
                for item in items:
                    chunks = self.chunk_precedent(item)
                    all_chunks.extend(chunks)
                stats["precedents"] += len(items)
            elif "interpretation" in filepath.name:
                for item in items:
                    chunks = self.chunk_interpretation(item)
                    all_chunks.extend(chunks)
                stats["interpretations"] += len(items)

        logger.info(f"\n📊 청킹 완료: {len(all_chunks)}개 청크")

        # 임베딩 생성 및 인덱싱
        if all_chunks:
            logger.info(f"\n🔄 임베딩 생성 중...")

            for i in range(0, len(all_chunks), batch_size):
                batch = all_chunks[i:i + batch_size]
                texts = [c.text for c in batch]
                ids = [c.id for c in batch]
                metadatas = [c.metadata for c in batch]

                # 임베딩 생성 (외부 API)
                embeddings = self._encode_batch(texts)

                # ChromaDB에 추가
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas
                )

                if (i + batch_size) % 500 == 0 or i + batch_size >= len(all_chunks):
                    logger.info(f"  인덱싱: {min(i + batch_size, len(all_chunks))}/{len(all_chunks)}")

        stats["chunks"] = len(all_chunks)

        logger.info(f"\n✅ 인덱싱 완료!")
        logger.info(f"  - 판례: {stats['precedents']}건")
        logger.info(f"  - 해석례: {stats['interpretations']}건")
        logger.info(f"  - 총 청크: {stats['chunks']}개")
        logger.info(f"  - 컬렉션: {self.collection_name}")
        logger.info(f"  - 저장 경로: {self.chroma_path}")

        return stats


def main():
    parser = argparse.ArgumentParser(description="판례/해석례 벡터DB 인덱싱")
    parser.add_argument(
        "--input", "-i",
        type=str,
        default="data/raw/categories",
        help="입력 디렉토리 (JSONL 파일 위치)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="vectordb",
        help="ChromaDB 저장 경로"
    )
    parser.add_argument(
        "--collection", "-c",
        type=str,
        default="law_cases",
        help="컬렉션 이름"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="특정 카테고리만 인덱싱 (예: labor)"
    )
    parser.add_argument(
        "--batch-size", "-b",
        type=int,
        default=100,
        help="배치 사이즈"
    )

    args = parser.parse_args()

    input_dir = PROJECT_ROOT / args.input
    output_dir = PROJECT_ROOT / args.output

    if not input_dir.exists():
        logger.error(f"입력 디렉토리가 존재하지 않습니다: {input_dir}")
        sys.exit(1)

    indexer = CaseIndexer(
        chroma_path=str(output_dir),
        collection_name=args.collection
    )

    stats = indexer.index_files(
        input_dir=input_dir,
        category_filter=args.category,
        batch_size=args.batch_size
    )

    logger.info(f"\n📋 인덱싱 결과: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    main()
