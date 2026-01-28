"""
LLM 추론 모듈 (llama-cpp-python)
Qwen2.5-7B-Instruct GGUF 모델 로드 및 추론
"""

import logging
from llama_cpp import Llama

logger = logging.getLogger(__name__)


class LLMManager:
    def __init__(self, model_path: str, n_ctx: int = 2048, n_threads: int = 4):
        """
        LLM 모델 초기화
        
        Args:
            model_path: GGUF 모델 파일 경로
            n_ctx: 컨텍스트 길이
            n_threads: 스레드 수
        """
        logger.info(f"Loading LLM from: {model_path}")
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False,
            )
            logger.info("LLM loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
    ) -> str:
        """
        텍스트 생성
        
        Args:
            prompt: 입력 프롬프트
            max_tokens: 최대 생성 토큰 수
            temperature: 샘플링 온도
            top_p: Top-p 샘플링 값
            
        Returns:
            생성된 텍스트
        """
        logger.debug(f"Generating response (prompt_len={len(prompt)})")
        try:
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )
            text = response["choices"][0]["text"].strip()
            logger.debug(f"Generated {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error during generation: {e}")
            raise
    
    def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
    ):
        """
        스트리밍 텍스트 생성
        
        Args:
            prompt: 입력 프롬프트
            max_tokens: 최대 생성 토큰 수
            temperature: 샘플링 온도
            top_p: Top-p 샘플링 값
            
        Yields:
            생성된 텍스트 청크
        """
        logger.debug(f"Streaming generation (prompt_len={len(prompt)})")
        try:
            for response in self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=True,
            ):
                chunk = response["choices"][0]["text"]
                if chunk:
                    yield chunk
        except Exception as e:
            logger.error(f"Error during streaming generation: {e}")
            raise
