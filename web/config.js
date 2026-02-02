/* ===========================
   LawBot Configuration
   환경별 설정 관리
   =========================== */

// API 엔드포인트 설정
const CONFIG = {
    // HuggingFace Spaces API 서버 URL
    API_BASE_URL: 'https://wonchulhee-korean-law-chatbot.hf.space',
};

// 현재 환경 감지 및 자동 설정
(function() {
    const hostname = window.location.hostname;

    // 로컬 개발 환경에서는 로컬 서버 사용
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        CONFIG.API_BASE_URL = 'http://localhost:7860';
    }

    // HuggingFace Spaces에서 직접 서빙하는 경우 (같은 도메인)
    if (hostname.includes('hf.space') || hostname.includes('huggingface.co')) {
        CONFIG.API_BASE_URL = '';  // 같은 도메인이므로 상대 경로 사용
    }

    // Vercel 랜딩 페이지에서는 HuggingFace API 호출 (기본값 유지)
    // lawbot-public.vercel.app -> wonchulhee-korean-law-chatbot.hf.space
})();

// API URL 가져오기 헬퍼 함수
function getApiUrl(endpoint) {
    const base = CONFIG.API_BASE_URL;
    if (!base) {
        return endpoint;
    }
    return base + endpoint;
}
