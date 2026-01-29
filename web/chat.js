/* ===========================
   Chat Page JavaScript
   홈페이지의 hero 채팅 기능과 동일한 구현
   =========================== */

// Initialize Lucide Icons
lucide.createIcons();

// API Endpoint
const API_BASE_URL = 'https://wonchulhee-korean-law-chatbot.hf.space';

// 분야별 정보
const CATEGORY_INTRO = {
    labor: {
        name: '노동법',
        icon: 'briefcase',
        color: '#3b82f6',
        message: '노동법 분야 상담을 시작합니다. 근로기준법, 최저임금법, 퇴직급여보장법 등을 기반으로 답변드립니다.',
    },
    housing: {
        name: '임대차법',
        icon: 'home',
        color: '#10b981',
        message: '임대차법 분야 상담을 시작합니다. 주택임대차보호법, 상가건물임대차보호법을 기반으로 답변드립니다.',
    },
    consumer: {
        name: '소비자보호법',
        icon: 'shield-check',
        color: '#f59e0b',
        message: '소비자보호법 분야 상담을 시작합니다. 소비자기본법, 전자상거래법을 기반으로 답변드립니다.',
    },
    traffic: {
        name: '교통사고',
        icon: 'car',
        color: '#ef4444',
        message: '교통사고·손해배상 분야 상담을 시작합니다. 자동차손해배상보장법, 도로교통법을 기반으로 답변드립니다.',
    },
};

// 분야별 예시 질문
const CATEGORY_EXAMPLES = {
    labor: [
        { label: '퇴직금 계산', question: '퇴직금은 어떻게 계산하나요?' },
        { label: '부당해고 대응', question: '부당해고를 당했을 때 어떻게 해야 하나요?' },
        { label: '임금체불', question: '임금을 받지 못했을 때 어떻게 해야 하나요?' },
    ],
    housing: [
        { label: '보증금 반환', question: '전세보증금을 돌려받지 못하면 어떻게 해야 하나요?' },
        { label: '계약갱신', question: '임대차 계약갱신청구권이 무엇인가요?' },
        { label: '대항력', question: '임차인의 대항력은 어떻게 갖추나요?' },
    ],
    consumer: [
        { label: '온라인 환불', question: '온라인 쇼핑 환불 규정이 어떻게 되나요?' },
        { label: '청약철회', question: '청약철회는 어떤 경우에 가능한가요?' },
        { label: '제품 하자', question: '제품에 하자가 있을 때 어떻게 보상받나요?' },
    ],
    traffic: [
        { label: '과실비율', question: '교통사고 과실비율은 어떻게 정해지나요?' },
        { label: '손해배상', question: '교통사고 손해배상은 어떻게 청구하나요?' },
        { label: '보험금 청구', question: '자동차 보험금 청구 절차가 어떻게 되나요?' },
    ],
};

// 법제처 법령 URL 매핑
const LAW_URLS = {
    "근로기준법": "https://www.law.go.kr/법령/근로기준법",
    "근로자퇴직급여보장법": "https://www.law.go.kr/법령/근로자퇴직급여보장법",
    "남녀고용평등과 일·가정 양립 지원에 관한 법률": "https://www.law.go.kr/법령/남녀고용평등과일·가정양립지원에관한법률",
    "최저임금법": "https://www.law.go.kr/법령/최저임금법",
    "산업재해보상보험법": "https://www.law.go.kr/법령/산업재해보상보험법",
    "주택임대차보호법": "https://www.law.go.kr/법령/주택임대차보호법",
    "상가건물임대차보호법": "https://www.law.go.kr/법령/상가건물임대차보호법",
    "소비자기본법": "https://www.law.go.kr/법령/소비자기본법",
    "전자상거래법": "https://www.law.go.kr/법령/전자상거래등에서의소비자보호에관한법률",
    "자동차손해배상보장법": "https://www.law.go.kr/법령/자동차손해배상보장법",
    "도로교통법": "https://www.law.go.kr/법령/도로교통법",
};

// State
let selectedCategory = null;
let conversationId = null;
let isLoading = false; // 중복 전송 방지

// DOM Elements
const chatInput = document.getElementById('chat-input');
const chatSubmit = document.getElementById('chat-submit');
const chatMessages = document.getElementById('chat-messages');
const categoryIndicator = document.getElementById('category-indicator');
const categoryIcon = document.getElementById('category-icon');
const categoryName = document.getElementById('category-name');
const changeCategoryBtn = document.getElementById('change-category-btn');
const chatCategoryHeader = document.getElementById('chat-category-header');

// URL에서 카테고리 가져오기
function getCategoryFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('category') || 'labor';
}

// 초기화
function init() {
    const category = getCategoryFromURL();

    if (CATEGORY_INTRO[category]) {
        selectCategory(category);
    } else {
        // 잘못된 카테고리면 홈으로 이동
        window.location.href = 'index.html';
    }
}

// 분야 선택
function selectCategory(category) {
    selectedCategory = category;
    conversationId = null;
    const info = CATEGORY_INTRO[category];

    // 헤더 업데이트
    categoryIndicator.className = 'category-indicator ' + category;
    categoryIcon.setAttribute('data-lucide', info.icon);
    categoryName.textContent = info.name;
    lucide.createIcons();

    // 채팅 메시지 초기화
    chatMessages.innerHTML = '';

    // 웰컴 메시지 표시 (홈페이지와 동일한 구조)
    showWelcomeScreen(category);
}

// 웰컴 화면 표시
function showWelcomeScreen(category) {
    const info = CATEGORY_INTRO[category];
    const examples = CATEGORY_EXAMPLES[category];

    const welcomeHtml = `
        <div class="chat-welcome">
            <div class="welcome-icon" style="background: ${info.color}20;">
                <i data-lucide="${info.icon}" class="icon-xl" style="color: ${info.color};"></i>
            </div>
            <h3 class="welcome-title" style="color: ${info.color};">${info.name} 상담</h3>
            <p class="welcome-subtitle">${info.message}</p>

            <p class="example-label">예시 질문을 클릭해 보세요</p>
            <div class="welcome-examples">
                ${examples.map(ex => `
                    <button class="example-btn" data-question="${ex.question}">
                        <i data-lucide="message-circle" class="icon-xs"></i>
                        <span>${ex.label}</span>
                    </button>
                `).join('')}
            </div>
        </div>
    `;

    chatMessages.innerHTML = welcomeHtml;
    lucide.createIcons();

    // 예시 버튼 이벤트 바인딩
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.dataset.question;
            chatInput.value = question;
            chatInput.dispatchEvent(new Event('input'));
            chatInput.focus();
            setTimeout(() => sendMessage(), 300);
        });
    });
}

// 출처 URL 생성
function getSourceUrl(source) {
    const trimmed = source.trim();

    // 판례
    if (trimmed.startsWith('판례 ')) {
        const caseNumber = trimmed.replace('판례 ', '').trim();
        return {
            type: 'precedent',
            url: `https://www.law.go.kr/LSW/precSc.do?menuId=7&subMenuId=67&tabMenuId=1&query=${encodeURIComponent(caseNumber)}`,
            label: trimmed
        };
    }

    // 법령해석례
    if (trimmed.startsWith('법령해석례 ')) {
        const expcNumber = trimmed.replace('법령해석례 ', '').trim();
        return {
            type: 'interpretation',
            url: `https://www.law.go.kr/LSW/precSc.do?menuId=7&subMenuId=67&tabMenuId=2&query=${encodeURIComponent(expcNumber)}`,
            label: trimmed
        };
    }

    // 법령명
    if (LAW_URLS[trimmed]) {
        return {
            type: 'law',
            url: LAW_URLS[trimmed],
            label: trimmed
        };
    }

    // 부분 일치
    for (const [key, url] of Object.entries(LAW_URLS)) {
        if (trimmed.includes(key) || key.includes(trimmed)) {
            return {
                type: 'law',
                url: url,
                label: key
            };
        }
    }

    // 기타 법령
    if (trimmed.includes('법') || trimmed.includes('령')) {
        return {
            type: 'law',
            url: `https://www.law.go.kr/법령/${encodeURIComponent(trimmed)}`,
            label: trimmed
        };
    }

    return null;
}

// API 응답을 HTML로 포맷팅
function formatApiResponse(data) {
    let answerHtml = data.answer
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');

    let html = `<p>${answerHtml}</p>`;

    // 출처 정보
    if (data.sources && data.sources.length > 0) {
        html += '<div class="source-section" style="margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">';
        html += '<p style="font-size: 0.85em; color: var(--color-primary-light); margin-bottom: 8px;"><strong>📚 참고 자료:</strong></p>';

        html += '<ul style="font-size: 0.8em; color: rgba(255,255,255,0.6); padding-left: 16px; margin-bottom: 12px;">';
        data.sources.forEach(source => {
            const sourceInfo = getSourceUrl(source);
            if (sourceInfo && sourceInfo.url) {
                html += `<li style="margin-bottom: 4px;">
                    <a href="${sourceInfo.url}" target="_blank" rel="noopener noreferrer"
                       style="color: rgba(255,255,255,0.7); text-decoration: underline; text-decoration-style: dotted;">
                        ${source}
                    </a>
                </li>`;
            } else {
                html += `<li style="margin-bottom: 4px;">${source}</li>`;
            }
        });
        html += '</ul>';

        // 원문 버튼
        html += '<div class="source-links" style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px;">';

        data.sources.forEach(source => {
            const sourceInfo = getSourceUrl(source);
            if (sourceInfo) {
                let btnColor, btnBg, btnBorder, icon;
                if (sourceInfo.type === 'precedent') {
                    btnColor = '#f59e0b';
                    btnBg = 'rgba(245, 158, 11, 0.1)';
                    btnBorder = 'rgba(245, 158, 11, 0.3)';
                    icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>';
                } else if (sourceInfo.type === 'interpretation') {
                    btnColor = '#10b981';
                    btnBg = 'rgba(16, 185, 129, 0.1)';
                    btnBorder = 'rgba(16, 185, 129, 0.3)';
                    icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>';
                } else {
                    btnColor = 'var(--color-primary-light)';
                    btnBg = 'rgba(59, 130, 246, 0.1)';
                    btnBorder = 'rgba(59, 130, 246, 0.3)';
                    icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>';
                }

                html += `<a href="${sourceInfo.url}" target="_blank" rel="noopener noreferrer"
                    class="source-link-btn"
                    style="display: inline-flex; align-items: center; gap: 4px; padding: 6px 12px;
                           font-size: 0.75em; color: ${btnColor}; background: ${btnBg};
                           border: 1px solid ${btnBorder}; border-radius: 6px;
                           text-decoration: none; transition: all 0.2s;">
                    ${icon}
                    ${sourceInfo.label} 원문
                </a>`;
            }
        });

        html += '</div>';
        html += '</div>';
    }

    // 면책 고지
    if (data.disclaimer) {
        html += `<p style="font-size: 0.8em; color: rgba(255,255,255,0.4); margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">
            ⚠️ ${data.disclaimer}
        </p>`;
    }

    return html;
}

// 메시지 추가
function addMessage(content, type) {
    // 웰컴 화면 숨기기
    const welcomeEl = chatMessages.querySelector('.chat-welcome');
    if (welcomeEl) {
        welcomeEl.style.display = 'none';
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? '나' : 'AI';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 타이핑 인디케이터 표시
function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = id;
    typingDiv.className = 'message message-ai';
    typingDiv.innerHTML = `
        <div class="message-avatar">AI</div>
        <div class="message-content" style="display: flex; gap: 4px; padding: 16px 20px;">
            <span class="typing-dot" style="animation: typingDot 1.4s infinite; animation-delay: 0s;"></span>
            <span class="typing-dot" style="animation: typingDot 1.4s infinite; animation-delay: 0.2s;"></span>
            <span class="typing-dot" style="animation: typingDot 1.4s infinite; animation-delay: 0.4s;"></span>
        </div>
    `;

    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return id;
}

// 타이핑 인디케이터 제거
function removeTypingIndicator(id) {
    const typingEl = document.getElementById(id);
    if (typingEl) {
        typingEl.remove();
    }
}

// 메시지 전송
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || !selectedCategory) return;

    // 중복 전송 방지
    if (isLoading) return;
    isLoading = true;

    // 사용자 메시지 추가
    addMessage(message, 'user');

    // 입력 초기화
    chatInput.value = '';
    chatInput.style.height = 'auto';
    chatSubmit.disabled = true;

    // 타이핑 인디케이터 표시
    const typingId = showTypingIndicator();

    // 분야 정보를 메시지에 추가
    const categoryInfo = CATEGORY_INTRO[selectedCategory];
    const contextMessage = `[${categoryInfo.name} 관련 질문] ${message}`;

    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: contextMessage,
                conversation_id: conversationId
            })
        });

        if (!response.ok) {
            throw new Error(`API 오류: ${response.status}`);
        }

        const data = await response.json();
        conversationId = data.conversation_id;

        removeTypingIndicator(typingId);
        addMessage(formatApiResponse(data), 'ai');

    } catch (error) {
        console.error('API 호출 실패:', error);
        removeTypingIndicator(typingId);

        const errorMessage = `
            <p>죄송합니다. 서버 연결에 문제가 발생했습니다.</p>
            <p style="font-size: 0.85em; color: rgba(255,255,255,0.5); margin-top: 12px;">
                잠시 후 다시 시도해 주세요. 서버가 시작 중일 수 있습니다.
            </p>
        `;
        addMessage(errorMessage, 'ai');
    } finally {
        isLoading = false;
    }
}

// 분야 변경 모달
function showCategoryModal() {
    let modal = document.querySelector('.category-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.className = 'category-modal';
        modal.innerHTML = `
            <div class="category-modal-backdrop"></div>
            <div class="category-modal-content">
                <div class="category-modal-header">
                    <h2>상담 분야 변경</h2>
                    <p>다른 분야로 상담을 시작합니다.</p>
                </div>
                <div class="category-modal-grid">
                    <button class="category-modal-btn labor" data-category="labor">
                        <i data-lucide="briefcase" class="icon-lg"></i>
                        <span class="category-modal-btn-name">노동법</span>
                        <span class="category-modal-btn-desc">해고, 임금, 퇴직금</span>
                    </button>
                    <button class="category-modal-btn housing" data-category="housing">
                        <i data-lucide="home" class="icon-lg"></i>
                        <span class="category-modal-btn-name">임대차법</span>
                        <span class="category-modal-btn-desc">보증금, 계약갱신</span>
                    </button>
                    <button class="category-modal-btn consumer" data-category="consumer">
                        <i data-lucide="shield-check" class="icon-lg"></i>
                        <span class="category-modal-btn-name">소비자보호법</span>
                        <span class="category-modal-btn-desc">환불, 청약철회</span>
                    </button>
                    <button class="category-modal-btn traffic" data-category="traffic">
                        <i data-lucide="car" class="icon-lg"></i>
                        <span class="category-modal-btn-name">교통사고</span>
                        <span class="category-modal-btn-desc">손해배상, 보험</span>
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // 이벤트 바인딩
        modal.querySelector('.category-modal-backdrop').addEventListener('click', closeCategoryModal);
        modal.querySelectorAll('.category-modal-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const newCategory = btn.dataset.category;
                changeCategory(newCategory);
                closeCategoryModal();
            });
        });
    }

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    lucide.createIcons();
}

function closeCategoryModal() {
    const modal = document.querySelector('.category-modal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function changeCategory(newCategory) {
    if (newCategory === selectedCategory) return;

    // URL 업데이트
    const url = new URL(window.location.href);
    url.searchParams.set('category', newCategory);
    window.history.pushState({}, '', url);

    // 분야 선택
    selectCategory(newCategory);
}

// 이벤트 리스너
if (chatInput && chatSubmit) {
    chatInput.addEventListener('input', () => {
        chatSubmit.disabled = chatInput.value.trim().length === 0;
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!chatSubmit.disabled) {
                sendMessage();
            }
        }
    });

    chatSubmit.addEventListener('click', sendMessage);
}

if (changeCategoryBtn) {
    changeCategoryBtn.addEventListener('click', showCategoryModal);
}

// Navigation scroll effect
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }
});

// Mobile menu toggle
const mobileToggle = document.querySelector('.nav-mobile-toggle');
const navLinks = document.querySelector('.nav-links');

if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
        const isOpening = !mobileToggle.classList.contains('active');
        mobileToggle.classList.toggle('active');
        navLinks.classList.toggle('active');

        if (isOpening) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    });

    navLinks.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            mobileToggle.classList.remove('active');
            navLinks.classList.remove('active');
            document.body.style.overflow = '';
        });
    });
}

// Particle canvas
const canvas = document.getElementById('particle-canvas');
if (canvas) {
    const ctx = canvas.getContext('2d');
    let particles = [];

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    function createParticles() {
        particles = [];
        const numParticles = Math.min(50, Math.floor(window.innerWidth / 30));
        for (let i = 0; i < numParticles; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 2 + 0.5,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                alpha: Math.random() * 0.3 + 0.1
            });
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(59, 130, 246, ${p.alpha})`;
            ctx.fill();
        });

        requestAnimationFrame(animate);
    }

    resizeCanvas();
    createParticles();
    animate();

    window.addEventListener('resize', () => {
        resizeCanvas();
        createParticles();
    });
}

// 타이핑 애니메이션 스타일 추가
const typingStyles = document.createElement('style');
typingStyles.textContent = `
    .typing-dot {
        width: 8px;
        height: 8px;
        background: var(--color-primary);
        border-radius: 50%;
        opacity: 0.3;
    }

    @keyframes typingDot {
        0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
        30% { opacity: 1; transform: translateY(-4px); }
    }
`;
document.head.appendChild(typingStyles);

// 초기화 실행
init();
