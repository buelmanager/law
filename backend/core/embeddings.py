"""
임베딩 모듈
HuggingFace Inference API를 사용하여 외부에서 임베딩 생성
로컬 모델 로딩 없이 API 호출로 처리 → 메모리 절약
"""

import os
import logging
import requests
import numpy as np

logger = logging.getLogger(__name__)

# HuggingFace Inference API 설정
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/"
HF_TOKEN = os.getenv("HF_TOKEN", "")


class EmbeddingsManager:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-large"):
        """
        외부 임베딩 API 초기화

        Args:
            model_name: HuggingFace 모델 이름
        """
        self.model_name = model_name
        self.api_url = f"{HF_API_URL}{model_name}"
        self.headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
        logger.info(f"Using external embedding API: {model_name}")

        if not HF_TOKEN:
            logger.warning("HF_TOKEN not set. API calls may be rate-limited.")

    def encode(self, text: str) -> np.ndarray:
        """
        단일 텍스트 임베딩 생성 (외부 API)

        Args:
            text: 입력 텍스트

        Returns:
            임베딩 벡터
        """
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
        배치 임베딩 생성 (외부 API)

        Args:
            texts: 입력 텍스트 리스트

        Returns:
            임베딩 벡터 리스트
        """
        embeddings = []
        for text in texts:
            embedding = self.encode(text)
            embeddings.append(embedding)
        return np.array(embeddings)
