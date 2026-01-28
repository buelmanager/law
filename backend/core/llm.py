"""
LLM 추론 모듈 (Groq API)
Groq의 빠른 추론 API를 사용하여 LLM 응답 생성
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

# Groq API 설정
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.1-8b-instant"  # 빠르고 좋은 성능


class LLMManager:
    def __init__(self, api_key: str = None, model: str = DEFAULT_MODEL):
        """
        Groq LLM 초기화

        Args:
            api_key: Groq API 키 (없으면 환경변수에서 로드)
            model: 사용할 모델명
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model

        if not self.api_key:
            logger.error("GROQ_API_KEY not found")
            raise ValueError("GROQ_API_KEY is required")

        logger.info(f"Groq LLM initialized with model: {self.model}")

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

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }

        try:
            response = requests.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            result = response.json()
            text = result["choices"][0]["message"]["content"].strip()
            logger.debug(f"Generated {len(text)} characters")
            return text

        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API error: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing Groq response: {e}")
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

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": True,
        }

        try:
            response = requests.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=60,
                stream=True,
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: ') and line != 'data: [DONE]':
                        import json
                        data = json.loads(line[6:])
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                yield content

        except Exception as e:
            logger.error(f"Error during streaming generation: {e}")
            raise
