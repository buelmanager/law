"""
임베딩 모듈
- 로컬 모델: sentence-transformers (e5-small, 경량)
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingsManager:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-base"):
        """
        임베딩 모델 초기화 (로컬 모델 사용)

        Args:
            model_name: HuggingFace 모델 이름
        """
        self.model_name = model_name
        self.local_model = None

        # 로컬 모델 로드
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local embeddings model: {model_name}")
            self.local_model = SentenceTransformer(model_name)
            logger.info("Local embeddings model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            raise

    def encode(self, text: str) -> np.ndarray:
        """
        단일 텍스트 임베딩 생성

        Args:
            text: 입력 텍스트

        Returns:
            임베딩 벡터
        """
        embedding = self.local_model.encode([text], convert_to_numpy=True)
        return embedding[0]

    def encode_batch(self, texts: list) -> np.ndarray:
        """
        배치 임베딩 생성

        Args:
            texts: 입력 텍스트 리스트

        Returns:
            임베딩 벡터 리스트
        """
        return self.local_model.encode(texts, convert_to_numpy=True)
