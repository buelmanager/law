---
title: Korean Law Chatbot
emoji: ⚖️
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# AI 법률 상담 챗봇

무료 클라우드 환경에서 운영되는 RAG 기반 노동법 전문 AI 상담 서비스입니다.

## 기능

- 노동법 관련 질문에 대한 AI 답변
- 관련 법령 조문 검색 및 인용
- 하이브리드 검색 (BM25 + 벡터)

## 기술 스택

- **LLM**: Qwen2.5-7B-Instruct (GGUF 4-bit)
- **임베딩**: multilingual-e5-large
- **벡터DB**: ChromaDB
- **백엔드**: FastAPI
- **프론트엔드**: Next.js 14

## 면책 고지

본 서비스는 AI가 제공하는 일반적인 법률 정보이며, 정식 법률 자문이 아닙니다.
구체적인 사안은 반드시 변호사와 상담하세요.

## 라이선스

MIT License
