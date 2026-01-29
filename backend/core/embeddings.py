"""
임베딩 모듈
- 로컬 모델: sentence-transformers (빌드 시 사용)
- 외부 API: HuggingFace Inference API (런타임 시 사용, 더 큰 모델 가능)
"""

import os
import logging
import requests
import numpy as np

logger = logging.getLogger(__name__)

# HuggingFace Inference API 설정
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/"
HF_TOKEN = os.getenv("HF_TOKEN", "")
USE_EXTERNAL_API = os.getenv("USE_EXTERNAL_EMBEDDING", "true").lower() == "true"


class EmbeddingsManager:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-large"):
        """
        임베딩 모델 초기화

        USE_EXTERNAL_EMBEDDING=true: 외부 API 사용 (e5-large 가능)
        USE_EXTERNAL_EMBEDDING=false: 로컬 모델 사용

        Args:
            model_name: HuggingFace 모델 이름
        """
        self.model_name = model_name
        self.use_external = USE_EXTERNAL_API
        self.local_model = None

        if self.use_external:
            self.api_url = f"{HF_API_URL}{model_name}"
            self.headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
            logger.info(f"Using external embedding API: {model_name}")
            if not HF_TOKEN:
                logger.warning("HF_TOKEN not set. API calls may be rate-limited.")
        else:
            # 로컬 모델 사용
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
        if self.use_external:
            return self._encode_external(text)
        else:
            embedding = self.local_model.encode([text], convert_to_numpy=True)
            return embedding[0]

    def _encode_external(self, text: str) -> np.ndarray:
        """외부 API로 임베딩 생성"""
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": text, "options": {"wait_for_model": True}},
                timeout=30
            )
            response.raise_for_status()
            embedding = response.json()

            # API 응답이 중첩 리스트일 수 있음
            if isinstance(embedding, list) and len(embedding) > 0:
                if isinstance(embedding[0], list):
                    # [[[...]]] → 평균 풀링
                    embedding = np.mean(embedding[0], axis=0)
                else:
                    embedding = np.array(embedding)

            return np.array(embedding)
        except Exception as e:
            logger.error(f"Embedding API error: {e}")
            # 폴백: 빈 벡터 반환 (1024 dims for e5-large)
            return np.zeros(1024)

    def encode_batch(self, texts: list) -> np.ndarray:
        """
        배치 임베딩 생성

        Args:
            texts: 입력 텍스트 리스트

        Returns:
            임베딩 벡터 리스트
        """
        if self.use_external:
            embeddings = [self._encode_external(text) for text in texts]
            return np.array(embeddings)
        else:
            return self.local_model.encode(texts, convert_to_numpy=True)
