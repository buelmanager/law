"""
LLM 추론 모듈 (Multi-Provider 지원)
Mistral AI (기본) 또는 Groq API를 사용하여 LLM 응답 생성
- Mistral: 월 10억 토큰, 분당 50만 토큰 (무료 티어 최고)
- Groq: 빠르지만 Rate limit 제한적
"""

import os
import logging
import time
import requests

logger = logging.getLogger(__name__)

# API 설정
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 기본 모델 설정
DEFAULT_MISTRAL_MODEL = "open-mixtral-8x7b"  # 무료 티어, 한국어 우수
DEFAULT_GROQ_MODEL = "llama-3.1-70b-versatile"


class LLMManager:
    def __init__(
        self,
        mistral_api_key: str = None,
        groq_api_key: str = None,
        provider: str = None,
        model: str = None,
    ):
        """
        LLM 초기화 (Mistral 우선, Groq 폴백)

        Args:
            mistral_api_key: Mistral API 키
            groq_api_key: Groq API 키 (폴백용)
            provider: 'mistral' 또는 'groq' (None이면 자동 선택)
            model: 사용할 모델명
        """
        self.mistral_api_key = mistral_api_key or os.getenv("MISTRAL_API_KEY")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")

        # Provider 자동 선택: Mistral 우선
        if provider:
            self.provider = provider
        elif self.mistral_api_key:
            self.provider = "mistral"
        elif self.groq_api_key:
            self.provider = "groq"
        else:
            logger.error("No API key found (MISTRAL_API_KEY or GROQ_API_KEY)")
            raise ValueError("MISTRAL_API_KEY or GROQ_API_KEY is required")

        # 모델 설정
        if model:
            self.model = model
        elif self.provider == "mistral":
            self.model = DEFAULT_MISTRAL_MODEL
        else:
            self.model = DEFAULT_GROQ_MODEL

        # API URL 설정
        if self.provider == "mistral":
            self.api_url = MISTRAL_API_URL
            self.api_key = self.mistral_api_key
        else:
            self.api_url = GROQ_API_URL
            self.api_key = self.groq_api_key

        logger.info(f"LLM initialized: provider={self.provider}, model={self.model}")

    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.95,
        max_retries: int = 3,
    ) -> str:
        """
        텍스트 생성 (재시도 로직 포함)

        Args:
            prompt: 입력 프롬프트
            max_tokens: 최대 생성 토큰 수
            temperature: 샘플링 온도
            top_p: Top-p 샘플링 값
            max_retries: 최대 재시도 횟수

        Returns:
            생성된 텍스트
        """
        logger.debug(f"Generating response (provider={self.provider}, prompt_len={len(prompt)})")

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

        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=60,
                )

                # Rate limit 처리 (429)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 10))
                    logger.warning(f"Rate limited, waiting {retry_after}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()

                result = response.json()
                text = result["choices"][0]["message"]["content"].strip()
                logger.debug(f"Generated {len(text)} characters")
                return text

            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"API error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing response: {e}")
                raise

        # 모든 재시도 실패 시
        logger.error(f"All {max_retries} attempts failed: {last_error}")
        raise last_error

    def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
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
        logger.debug(f"Streaming generation (provider={self.provider}, prompt_len={len(prompt)})")

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
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120,
                stream=True,
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: ') and line != 'data: [DONE]':
                        import json
                        try:
                            data = json.loads(line[6:])
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Error during streaming generation: {e}")
            raise
