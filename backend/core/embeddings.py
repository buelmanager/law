"""
임베딩 모듈
multilingual-e5-large 또는 ko-sroberta 사용
"""

import logging
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingsManager:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-large"):
        """
        임베딩 모델 초기화
        
        Args:
            model_name: HuggingFace 모델 이름
        """
        logger.info(f"Loading embeddings model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info("Embeddings model loaded successfully")
    
    def encode(self, text: str) -> np.ndarray:
        """
        단일 텍스트 임베딩 생성
        
        Args:
            text: 입력 텍스트
            
        Returns:
            임베딩 벡터
        """
        embedding = self.model.encode([text], convert_to_numpy=True)
        return embedding[0]
    
    def encode_batch(self, texts: list) -> np.ndarray:
        """
        배치 임베딩 생성
        
        Args:
            texts: 입력 텍스트 리스트
            
        Returns:
            임베딩 벡터 리스트
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
