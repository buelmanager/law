/* ===========================
   LawBot Configuration
   환경별 설정 관리
   =========================== */

// API 엔드포인트 설정
// 배포 시 이 값을 환경에 맞게 변경하세요
const CONFIG = {
    // API 서버 URL (빈 문자열이면 같은 도메인 사용)
    API_BASE_URL: '',

    // 개발 환경에서 로컬 서버 사용 시
    // API_BASE_URL: 'http://localhost:7860',
};

// 현재 환경 감지 및 자동 설정
(function() {
    const hostname = window.location.hostname;

    // 로컬 개발 환경
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        CONFIG.API_BASE_URL = CONFIG.API_BASE_URL || 'http://localhost:7860';
    }

    // 프로덕션 환경 (같은 도메인에서 API 서빙 시 빈 문자열 유지)
    // HuggingFace Spaces나 같은 서버에서 서빙하는 경우
})();

// API URL 가져오기 헬퍼 함수
function getApiUrl(endpoint) {
    const base = CONFIG.API_BASE_URL;
    if (!base) {
        return endpoint;
    }
    return base + endpoint;
}
