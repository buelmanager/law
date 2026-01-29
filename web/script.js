/* ===========================
   LawBot - Main Script
   4대 법률 분야 특화 AI 법률 정보 서비스
   GSAP + Lenis + Canvas Particles + Lucide Icons
   =========================== */

// Initialize Lucide Icons
lucide.createIcons();

// Initialize Lenis Smooth Scroll
const lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    direction: 'vertical',
    gestureDirection: 'vertical',
    smooth: true,
    smoothTouch: false,
    touchMultiplier: 2,
    prevent: (node) => {
        // 채팅 메시지 영역에서는 Lenis 스크롤 비활성화
        return node.closest('.chat-messages') !== null ||
               node.closest('.chat-container') !== null ||
               node.classList.contains('chat-messages');
    }
});

// Register GSAP Plugins
gsap.registerPlugin(ScrollTrigger);

// Sync Lenis with GSAP ticker
gsap.ticker.add((time) => {
    lenis.raf(time * 1000);
});

gsap.ticker.lagSmoothing(0);

// Update ScrollTrigger on Lenis scroll
lenis.on('scroll', ScrollTrigger.update);

// 채팅 영역에서 휠 이벤트가 페이지 스크롤로 전파되지 않도록 처리
document.addEventListener('DOMContentLoaded', () => {
    const chatMessagesEl = document.getElementById('chat-messages');
    if (chatMessagesEl) {
        chatMessagesEl.addEventListener('wheel', (e) => {
            const { scrollTop, scrollHeight, clientHeight } = chatMessagesEl;
            const isScrolledToTop = scrollTop === 0;
            const isScrolledToBottom = scrollTop + clientHeight >= scrollHeight - 1;

            // 스크롤이 위나 아래 끝에 도달했을 때만 이벤트 전파 방지
            if ((e.deltaY < 0 && isScrolledToTop) || (e.deltaY > 0 && isScrolledToBottom)) {
                // 끝에 도달해도 페이지 스크롤 방지
                e.preventDefault();
            }
            // 채팅 영역 내에서는 항상 이벤트 전파 중단
            e.stopPropagation();
        }, { passive: false });
    }
});

/* ===========================
   Particle Canvas Animation
   =========================== */
class ParticleNetwork {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: null, y: null, radius: 150 };
        this.particleCount = 60;
        this.connectionDistance = 120;
        this.colors = {
            particle: '#3b82f6',
            connection: 'rgba(59, 130, 246, 0.08)',
        };

        this.init();
        this.animate();
        this.addEventListeners();
    }

    init() {
        this.resize();

        for (let i = 0; i < this.particleCount; i++) {
            this.particles.push(new Particle(this));
        }
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    addEventListeners() {
        window.addEventListener('resize', () => {
            this.resize();
        });

        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });

        window.addEventListener('mouseout', () => {
            this.mouse.x = null;
            this.mouse.y = null;
        });
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.particles.forEach((particle) => {
            particle.update();
            particle.draw();
        });

        this.drawConnections();

        requestAnimationFrame(() => this.animate());
    }

    drawConnections() {
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.connectionDistance) {
                    const opacity = 1 - distance / this.connectionDistance;
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = `rgba(59, 130, 246, ${opacity * 0.15})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.stroke();
                }
            }
        }
    }
}

class Particle {
    constructor(network) {
        this.network = network;
        this.x = Math.random() * network.canvas.width;
        this.y = Math.random() * network.canvas.height;
        this.vx = (Math.random() - 0.5) * 0.3;
        this.vy = (Math.random() - 0.5) * 0.3;
        this.radius = Math.random() * 2 + 1;
        this.baseRadius = this.radius;
    }

    update() {
        if (this.network.mouse.x !== null && this.network.mouse.y !== null) {
            const dx = this.network.mouse.x - this.x;
            const dy = this.network.mouse.y - this.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < this.network.mouse.radius) {
                const force = (this.network.mouse.radius - distance) / this.network.mouse.radius;
                const angle = Math.atan2(dy, dx);
                this.vx -= Math.cos(angle) * force * 0.015;
                this.vy -= Math.sin(angle) * force * 0.015;
                this.radius = this.baseRadius + force * 1.5;
            } else {
                this.radius = this.baseRadius;
            }
        }

        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 0 || this.x > this.network.canvas.width) this.vx *= -1;
        if (this.y < 0 || this.y > this.network.canvas.height) this.vy *= -1;

        this.vx *= 0.995;
        this.vy *= 0.995;

        if (Math.abs(this.vx) < 0.05) this.vx = (Math.random() - 0.5) * 0.3;
        if (Math.abs(this.vy) < 0.05) this.vy = (Math.random() - 0.5) * 0.3;
    }

    draw() {
        this.network.ctx.beginPath();
        this.network.ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        this.network.ctx.fillStyle = this.network.colors.particle;
        this.network.ctx.globalAlpha = 0.4;
        this.network.ctx.fill();
        this.network.ctx.globalAlpha = 1;
    }
}

// Initialize Particle Network
const canvas = document.getElementById('particle-canvas');
if (canvas) {
    new ParticleNetwork(canvas);
}

/* ===========================
   Navigation Scroll Effect
   =========================== */
const nav = document.querySelector('.nav');

ScrollTrigger.create({
    start: 'top -100',
    onUpdate: (self) => {
        if (self.direction === 1 && self.scroll() > 100) {
            nav.classList.add('scrolled');
        } else if (self.scroll() < 100) {
            nav.classList.remove('scrolled');
        }
    },
});

/* ===========================
   Hero Animations
   =========================== */
const heroTimeline = gsap.timeline({ defaults: { ease: 'power3.out' } });

heroTimeline
    .to('.hero-badge', {
        opacity: 1,
        y: 0,
        duration: 0.8,
        delay: 0.3,
    })
    .to(
        '.hero-areas',
        {
            opacity: 1,
            y: 0,
            duration: 0.8,
        },
        '-=0.5'
    )
    .to(
        '.title-line',
        {
            opacity: 1,
            y: 0,
            duration: 1,
            stagger: 0.15,
        },
        '-=0.4'
    )
    .to(
        '.hero-description',
        {
            opacity: 1,
            y: 0,
            duration: 0.8,
        },
        '-=0.6'
    )
    .to(
        '.hero-trust',
        {
            opacity: 1,
            y: 0,
            duration: 0.8,
        },
        '-=0.5'
    )
    .to(
        '.hero-ai-notice',
        {
            opacity: 1,
            y: 0,
            duration: 0.8,
        },
        '-=0.5'
    )
    .to(
        '.hero-chat',
        {
            opacity: 1,
            y: 0,
            duration: 1,
        },
        '-=0.6'
    );

// Set initial state for hero-chat
gsap.set('.hero-chat', { opacity: 0, y: 30 });

/* ===========================
   Blur Reveal Animation
   =========================== */
const blurElements = document.querySelectorAll('.blur-reveal');

blurElements.forEach((el) => {
    gsap.to(el, {
        scrollTrigger: {
            trigger: el,
            start: 'top 85%',
            toggleActions: 'play none none none',
        },
        opacity: 1,
        filter: 'blur(0px)',
        y: 0,
        duration: 1,
        ease: 'power3.out',
    });
});

/* ===========================
   Trust Cards Animation
   =========================== */
const trustCards = document.querySelectorAll('.trust-card');

trustCards.forEach((card, index) => {
    gsap.to(card, {
        scrollTrigger: {
            trigger: card,
            start: 'top 85%',
            toggleActions: 'play none none none',
        },
        opacity: 1,
        y: 0,
        duration: 0.8,
        delay: index * 0.1,
        ease: 'power3.out',
    });
});

/* ===========================
   Feature Cards Animation
   =========================== */
const featureCards = document.querySelectorAll('.feature-card');

featureCards.forEach((card, index) => {
    gsap.to(card, {
        scrollTrigger: {
            trigger: card,
            start: 'top 85%',
            toggleActions: 'play none none none',
        },
        opacity: 1,
        y: 0,
        duration: 0.8,
        delay: index * 0.1,
        ease: 'power3.out',
    });
});

/* ===========================
   RAG Steps Animation
   =========================== */
const ragSteps = document.querySelectorAll('.rag-step');
const ragArrows = document.querySelectorAll('.rag-arrow');

ragSteps.forEach((step, index) => {
    gsap.to(step, {
        scrollTrigger: {
            trigger: step,
            start: 'top 85%',
            toggleActions: 'play none none none',
        },
        opacity: 1,
        y: 0,
        duration: 0.8,
        delay: index * 0.15,
        ease: 'power3.out',
    });
});

ragArrows.forEach((arrow, index) => {
    gsap.to(arrow, {
        scrollTrigger: {
            trigger: arrow,
            start: 'top 85%',
            toggleActions: 'play none none none',
        },
        opacity: 0.5,
        duration: 0.8,
        delay: index * 0.15 + 0.2,
        ease: 'power3.out',
    });
});

/* ===========================
   Category Area Cards Animation
   =========================== */
const categoryAreas = document.querySelectorAll('.category-area');

categoryAreas.forEach((card, index) => {
    gsap.to(card, {
        scrollTrigger: {
            trigger: card,
            start: 'top 85%',
            toggleActions: 'play none none none',
        },
        opacity: 1,
        y: 0,
        duration: 0.8,
        delay: index * 0.15,
        ease: 'power3.out',
    });
});

/* ===========================
   Smooth Scroll Links
   =========================== */
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            lenis.scrollTo(target, {
                offset: -100,
                duration: 1.2,
            });
        }
    });
});

/* ===========================
   Chat Functionality
   =========================== */
const API_BASE_URL = 'https://wonchulhee-korean-law-chatbot.hf.space';
let conversationId = null;
let selectedCategory = null;

const chatInput = document.getElementById('chat-input');
const chatSubmit = document.getElementById('chat-submit');
const chatMessages = document.getElementById('chat-messages');
const categorySelect = document.getElementById('category-select');
const welcomeExamples = document.getElementById('welcome-examples');
const exampleBtnsContainer = document.getElementById('example-btns');

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

// 분야별 안내 메시지
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
        icon: 'shopping-cart',
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

// 분야 선택 버튼 이벤트
if (categorySelect) {
    const categoryBtns = categorySelect.querySelectorAll('.category-btn');
    categoryBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const category = btn.dataset.category;
            selectCategory(category);
        });
    });
}

function selectCategory(category) {
    selectedCategory = category;
    const info = CATEGORY_INTRO[category];

    // 분야 변경 버튼 표시
    const changeCategoryBtn = document.getElementById('change-category-btn');
    if (changeCategoryBtn) {
        changeCategoryBtn.style.display = 'flex';
    }

    // 선택된 버튼 하이라이트
    const currentCategorySelect = document.getElementById('category-select');
    if (currentCategorySelect) {
        const categoryBtns = currentCategorySelect.querySelectorAll('.category-btn');
        categoryBtns.forEach(btn => {
            btn.classList.remove('selected');
            if (btn.dataset.category === category) {
                btn.classList.add('selected');
            }
        });
    }

    // 예시 질문 표시
    if (welcomeExamples && exampleBtnsContainer) {
        welcomeExamples.style.display = 'block';
        exampleBtnsContainer.innerHTML = '';

        CATEGORY_EXAMPLES[category].forEach(example => {
            const btn = document.createElement('button');
            btn.className = 'example-btn';
            btn.dataset.question = example.question;
            btn.innerHTML = `<i data-lucide="message-circle" class="icon-xs"></i> ${example.label}`;
            btn.addEventListener('click', () => {
                if (chatInput) {
                    chatInput.value = example.question;
                    chatInput.dispatchEvent(new Event('input'));
                    chatInput.focus();
                    setTimeout(() => sendMessage(), 300);
                }
            });
            exampleBtnsContainer.appendChild(btn);
        });

        // Lucide 아이콘 재초기화
        lucide.createIcons();
    }

    // 채팅창 확장 및 안내 메시지 표시
    const heroSection = document.querySelector('.hero.hero-with-chat');
    if (heroSection && !heroSection.classList.contains('chat-fullwidth')) {
        heroSection.classList.add('chat-fullwidth');
    }

    const chatContainer = document.querySelector('.hero-chat .chat-container');
    if (chatContainer && !chatContainer.classList.contains('chat-expanded')) {
        chatContainer.classList.add('chat-expanded');
    }

    // 분야 선택 안내 메시지를 AI 메시지로 추가
    const welcomeEl = chatMessages.querySelector('.chat-welcome');
    if (welcomeEl) {
        welcomeEl.style.display = 'none';
    }

    // 분야 선택 메시지 추가
    const introMessage = `
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 8px; background: ${info.color}20;">
                <i data-lucide="${info.icon}" style="width: 18px; height: 18px; color: ${info.color};"></i>
            </span>
            <strong style="color: ${info.color};">${info.name}</strong> 상담
        </div>
        <p>${info.message}</p>
        <p style="font-size: 0.85em; color: rgba(255,255,255,0.5); margin-top: 12px;">아래 예시 질문을 클릭하거나 직접 질문을 입력해 주세요.</p>
    `;
    addMessage(introMessage, 'ai');

    // Lucide 아이콘 재초기화
    lucide.createIcons();
}

// 분야 변경 버튼
const changeCategoryBtn = document.getElementById('change-category-btn');

if (changeCategoryBtn) {
    changeCategoryBtn.addEventListener('click', () => {
        resetCategory();
    });
}

function resetCategory() {
    selectedCategory = null;
    conversationId = null;

    // 분야 변경 버튼 숨기기
    if (changeCategoryBtn) {
        changeCategoryBtn.style.display = 'none';
    }

    // 채팅 메시지 초기화
    if (chatMessages) {
        chatMessages.innerHTML = '';

        // 웰컴 화면 다시 표시
        const welcomeHtml = `
            <div class="chat-welcome">
                <div class="welcome-icon">
                    <i data-lucide="scale" class="icon-xl"></i>
                </div>
                <h3>LawBot에 오신 것을 환영합니다</h3>
                <p>상담받고 싶은 법률 분야를 선택해 주세요.</p>

                <div class="category-select" id="category-select">
                    <button class="category-btn labor" data-category="labor">
                        <i data-lucide="briefcase" class="icon-md"></i>
                        <span class="category-name">노동법</span>
                        <span class="category-desc">부당해고, 임금체불, 퇴직금</span>
                    </button>
                    <button class="category-btn housing" data-category="housing">
                        <i data-lucide="home" class="icon-md"></i>
                        <span class="category-name">임대차법</span>
                        <span class="category-desc">보증금 반환, 계약갱신</span>
                    </button>
                    <button class="category-btn consumer" data-category="consumer">
                        <i data-lucide="shopping-cart" class="icon-md"></i>
                        <span class="category-name">소비자보호법</span>
                        <span class="category-desc">환불, 청약철회, 제품 하자</span>
                    </button>
                    <button class="category-btn traffic" data-category="traffic">
                        <i data-lucide="car" class="icon-md"></i>
                        <span class="category-name">교통사고</span>
                        <span class="category-desc">과실비율, 손해배상</span>
                    </button>
                </div>

                <div class="welcome-examples" id="welcome-examples" style="display: none;">
                    <span class="example-label">예시 질문:</span>
                    <div class="example-btns" id="example-btns"></div>
                </div>
            </div>
        `;
        chatMessages.innerHTML = welcomeHtml;

        // 아이콘 재초기화
        lucide.createIcons();

        // 카테고리 버튼 이벤트 다시 바인딩
        const newCategorySelect = document.getElementById('category-select');
        if (newCategorySelect) {
            const newCategoryBtns = newCategorySelect.querySelectorAll('.category-btn');
            newCategoryBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const category = btn.dataset.category;
                    selectCategory(category);
                });
            });
        }
    }

    // 채팅창 축소
    const heroSection = document.querySelector('.hero.hero-with-chat');
    if (heroSection) {
        heroSection.classList.remove('chat-fullwidth');
    }

    const chatContainer = document.querySelector('.hero-chat .chat-container');
    if (chatContainer) {
        chatContainer.classList.remove('chat-expanded');
    }
}

// 기존 예시 버튼 (폴백용)
const exampleBtns = document.querySelectorAll('.example-btn:not(#example-btns .example-btn)');

// Enable/disable submit button based on input
if (chatInput && chatSubmit) {
    chatInput.addEventListener('input', () => {
        chatSubmit.disabled = chatInput.value.trim().length === 0;

        // Auto-resize textarea
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    // Handle Enter key (Shift+Enter for new line)
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

// Example button click handlers
exampleBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
        const question = btn.dataset.question;
        if (chatInput) {
            chatInput.value = question;
            chatInput.dispatchEvent(new Event('input'));

            // Focus input and send
            chatInput.focus();
            setTimeout(() => {
                sendMessage();
            }, 300);
        }
    });
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // 분야가 선택되지 않은 경우 경고
    if (!selectedCategory) {
        alert('먼저 상담받고 싶은 법률 분야를 선택해 주세요.');
        return;
    }

    // Expand chat to full width when conversation starts
    const heroSection = document.querySelector('.hero.hero-with-chat');
    if (heroSection && !heroSection.classList.contains('chat-fullwidth')) {
        heroSection.classList.add('chat-fullwidth');
    }

    // Expand chat container when conversation starts
    const chatContainer = document.querySelector('.hero-chat .chat-container');
    if (chatContainer && !chatContainer.classList.contains('chat-expanded')) {
        chatContainer.classList.add('chat-expanded');
    }

    // Hide welcome message
    const welcomeEl = chatMessages.querySelector('.chat-welcome');
    if (welcomeEl) {
        welcomeEl.style.display = 'none';
    }

    // Add user message
    addMessage(message, 'user');

    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';
    chatSubmit.disabled = true;

    // Show typing indicator
    const typingId = showTypingIndicator();

    // 분야 정보를 메시지에 추가 (선택 사항)
    const categoryInfo = CATEGORY_INTRO[selectedCategory];
    const contextMessage = `[${categoryInfo.name} 관련 질문] ${message}`;

    try {
        // 실제 API 호출
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

        // AI 응답 표시
        removeTypingIndicator(typingId);
        addMessage(formatApiResponse(data), 'ai');
    } catch (error) {
        console.error('API 호출 실패:', error);
        removeTypingIndicator(typingId);

        // API 실패 시 폴백: 에러 메시지 또는 데모 응답
        const errorMessage = `
            <p>죄송합니다. 서버 연결에 문제가 발생했습니다.</p>
            <p style="font-size: 0.85em; color: rgba(255,255,255,0.5); margin-top: 12px;">
                잠시 후 다시 시도해 주세요. 서버가 시작 중일 수 있습니다.
            </p>
        `;
        addMessage(errorMessage, 'ai');
    }
}

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

// 출처 유형 판별 및 URL 생성
function getSourceUrl(source) {
    const trimmed = source.trim();

    // 판례 (예: "판례 2018다244877", "판례 2024노652")
    if (trimmed.startsWith('판례 ')) {
        const caseNumber = trimmed.replace('판례 ', '').trim();
        // 대법원 종합법률정보 판례 검색
        return {
            type: 'precedent',
            url: `https://glaw.scourt.go.kr/wsjo/panre/sjo100.do?q=${encodeURIComponent(caseNumber)}`,
            label: trimmed
        };
    }

    // 법령해석례 (예: "법령해석례 21-0702", "법령해석례 07-0115")
    if (trimmed.startsWith('법령해석례 ')) {
        const expcNumber = trimmed.replace('법령해석례 ', '').trim();
        // 법제처 법령해석례 검색
        return {
            type: 'interpretation',
            url: `https://www.law.go.kr/LSW/precInfoP.do?q=${encodeURIComponent(expcNumber)}`,
            label: trimmed
        };
    }

    // 법령명인 경우
    if (LAW_URLS[trimmed]) {
        return {
            type: 'law',
            url: LAW_URLS[trimmed],
            label: trimmed
        };
    }

    // 부분 일치 검색
    for (const [key, url] of Object.entries(LAW_URLS)) {
        if (trimmed.includes(key) || key.includes(trimmed)) {
            return {
                type: 'law',
                url: url,
                label: key
            };
        }
    }

    // 기타 법령 (기본 검색)
    if (trimmed.includes('법') || trimmed.includes('령')) {
        return {
            type: 'law',
            url: `https://www.law.go.kr/법령/${encodeURIComponent(trimmed)}`,
            label: trimmed
        };
    }

    return null;
}

// 법령명에서 URL 가져오기 (기존 함수 유지 - 호환성)
function getLawUrl(lawName) {
    // 정확히 일치하는 경우
    if (LAW_URLS[lawName]) {
        return LAW_URLS[lawName];
    }
    // 부분 일치 검색
    for (const [key, url] of Object.entries(LAW_URLS)) {
        if (lawName.includes(key) || key.includes(lawName)) {
            return url;
        }
    }
    // 기본 검색 URL
    return `https://www.law.go.kr/법령/${encodeURIComponent(lawName)}`;
}

// 출처에서 법령명 추출 (출처 자체가 법령명인 경우도 처리)
function extractLawNames(sources) {
    const lawNames = new Set();

    // 알려진 법령명 목록
    const knownLaws = [
        "근로기준법",
        "근로자퇴직급여보장법",
        "남녀고용평등과 일·가정 양립 지원에 관한 법률",
        "최저임금법",
        "산업재해보상보험법",
        "주택임대차보호법",
        "상가건물임대차보호법",
        "소비자기본법",
        "전자상거래법",
        "자동차손해배상보장법",
        "도로교통법",
    ];

    sources.forEach(source => {
        const trimmedSource = source.trim();

        // 출처 자체가 법령명인 경우 (정확히 일치 또는 포함)
        knownLaws.forEach(law => {
            if (trimmedSource.includes(law) || law.includes(trimmedSource) || trimmedSource === law) {
                lawNames.add(law);
            }
        });

        // 부분 문자열 매칭 (예: "남녀고용평등" -> "남녀고용평등과 일·가정 양립 지원에 관한 법률")
        if (trimmedSource.includes("남녀고용평등") || trimmedSource.includes("고용평등")) {
            lawNames.add("남녀고용평등과 일·가정 양립 지원에 관한 법률");
        }
        if (trimmedSource.includes("전자상거래")) {
            lawNames.add("전자상거래법");
        }

        // 출처가 알려진 법령에 없으면 그대로 추가 (기본 URL로 연결)
        if (lawNames.size === 0 && trimmedSource.includes("법")) {
            lawNames.add(trimmedSource);
        }
    });

    // 출처를 그대로 법령명으로 사용 (매칭이 안된 경우)
    if (lawNames.size === 0) {
        sources.forEach(source => {
            const trimmedSource = source.trim();
            if (trimmedSource && trimmedSource.length > 0) {
                lawNames.add(trimmedSource);
            }
        });
    }

    return Array.from(lawNames);
}

// API 응답을 HTML로 포맷팅
function formatApiResponse(data) {
    // 답변 텍스트를 HTML로 변환 (줄바꿈 처리)
    let answerHtml = data.answer
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');

    let html = `<p>${answerHtml}</p>`;

    // 출처 정보가 있으면 표시
    if (data.sources && data.sources.length > 0) {
        html += '<div class="source-section" style="margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">';
        html += '<p style="font-size: 0.85em; color: var(--color-primary-light); margin-bottom: 8px;"><strong>📚 참고 자료:</strong></p>';

        // 출처별 리스트 (클릭 가능한 링크로)
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

        // 출처별 원문 버튼
        html += '<div class="source-links" style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px;">';

        data.sources.forEach(source => {
            const sourceInfo = getSourceUrl(source);
            if (sourceInfo) {
                // 유형별 색상 설정
                let btnColor, btnBg, btnBorder, icon;
                if (sourceInfo.type === 'precedent') {
                    btnColor = '#f59e0b'; // 골드 - 판례
                    btnBg = 'rgba(245, 158, 11, 0.1)';
                    btnBorder = 'rgba(245, 158, 11, 0.3)';
                    icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>'; // 판례 아이콘
                } else if (sourceInfo.type === 'interpretation') {
                    btnColor = '#10b981'; // 에메랄드 - 해석례
                    btnBg = 'rgba(16, 185, 129, 0.1)';
                    btnBorder = 'rgba(16, 185, 129, 0.3)';
                    icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>'; // 문서 아이콘
                } else {
                    btnColor = 'var(--color-primary-light)'; // 블루 - 법령
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

// 인덱싱된 법령 데이터 다운로드
async function downloadLawData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/download/laws.json`);
        if (!response.ok) throw new Error('다운로드 실패');

        const data = await response.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = 'lawbot_indexed_laws.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('다운로드 오류:', error);
        alert('데이터 다운로드에 실패했습니다. 잠시 후 다시 시도해주세요.');
    }
}

function addMessage(content, type) {
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

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

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

function removeTypingIndicator(id) {
    const typingEl = document.getElementById(id);
    if (typingEl) {
        typingEl.remove();
    }
}

// Add typing animation styles
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

// Demo responses (for demonstration purposes)
function getDemoResponse(question) {
    const q = question.toLowerCase();

    if (q.includes('퇴직금') && q.includes('계산')) {
        return `
            <p><strong>퇴직금 계산 방법</strong></p>
            <p>퇴직금은 다음 공식으로 계산됩니다:</p>
            <p style="background: rgba(59,130,246,0.1); padding: 12px; border-radius: 8px; margin: 12px 0;">
                <strong>퇴직금 = 1일 평균임금 × 30일 × (재직일수 ÷ 365)</strong>
            </p>
            <p><strong>관련 법령:</strong> 근로자퇴직급여 보장법 제8조</p>
            <p style="font-size: 0.85em; color: rgba(255,255,255,0.5); margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">
                ⚠️ 위 정보는 일반적인 법률 정보이며, 구체적인 사안은 변호사와 상담하시기 바랍니다.
            </p>
        `;
    }

    if (q.includes('부당해고')) {
        return `
            <p><strong>부당해고 대응 방법</strong></p>
            <p>부당해고를 당했을 경우 다음과 같이 대응할 수 있습니다:</p>
            <ol style="margin: 12px 0; padding-left: 20px;">
                <li style="margin-bottom: 8px;">해고 사유와 날짜가 명시된 <strong>해고통지서</strong>를 요청하세요.</li>
                <li style="margin-bottom: 8px;">해고일로부터 <strong>3개월 이내</strong>에 노동위원회에 구제신청을 할 수 있습니다.</li>
                <li style="margin-bottom: 8px;">사업장 관할 <strong>지방노동위원회</strong>에 부당해고 구제신청서를 제출하세요.</li>
            </ol>
            <p><strong>관련 법령:</strong> 근로기준법 제23조, 제28조</p>
            <p style="font-size: 0.85em; color: rgba(255,255,255,0.5); margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">
                ⚠️ 위 정보는 일반적인 법률 정보이며, 구체적인 사안은 변호사와 상담하시기 바랍니다.
            </p>
        `;
    }

    if (q.includes('보증금') || q.includes('전세')) {
        return `
            <p><strong>전세보증금 반환 방법</strong></p>
            <p>전세보증금을 돌려받지 못할 경우 다음 절차를 진행할 수 있습니다:</p>
            <ol style="margin: 12px 0; padding-left: 20px;">
                <li style="margin-bottom: 8px;"><strong>내용증명 발송:</strong> 임대인에게 보증금 반환을 요청하는 내용증명을 보내세요.</li>
                <li style="margin-bottom: 8px;"><strong>임차권등기명령:</strong> 법원에 임차권등기명령을 신청하여 대항력을 유지하세요.</li>
                <li style="margin-bottom: 8px;"><strong>지급명령 신청:</strong> 법원에 지급명령을 신청하거나 민사소송을 제기할 수 있습니다.</li>
            </ol>
            <p><strong>관련 법령:</strong> 주택임대차보호법 제3조, 제3조의3</p>
            <p style="font-size: 0.85em; color: rgba(255,255,255,0.5); margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">
                ⚠️ 위 정보는 일반적인 법률 정보이며, 구체적인 사안은 변호사와 상담하시기 바랍니다.
            </p>
        `;
    }

    if (q.includes('환불') || q.includes('청약철회')) {
        return `
            <p><strong>온라인 쇼핑 환불 규정</strong></p>
            <p>전자상거래법에 따른 청약철회 규정입니다:</p>
            <ul style="margin: 12px 0; padding-left: 20px;">
                <li style="margin-bottom: 8px;"><strong>청약철회 기간:</strong> 상품을 받은 날로부터 7일 이내</li>
                <li style="margin-bottom: 8px;"><strong>환불 기한:</strong> 청약철회 후 3영업일 이내 환불</li>
                <li style="margin-bottom: 8px;"><strong>배송비:</strong> 단순 변심은 소비자 부담, 하자는 판매자 부담</li>
            </ul>
            <p><strong>관련 법령:</strong> 전자상거래법 제17조</p>
            <p style="font-size: 0.85em; color: rgba(255,255,255,0.5); margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">
                ⚠️ 위 정보는 일반적인 법률 정보이며, 구체적인 사안은 변호사와 상담하시기 바랍니다.
            </p>
        `;
    }

    // Default response
    return `
        <p>질문해 주셔서 감사합니다.</p>
        <p>현재 데모 버전에서는 제한된 응답만 제공됩니다. 실제 서비스에서는 법령과 판례를 기반으로 더 상세한 답변을 받으실 수 있습니다.</p>
        <p><strong>지원되는 예시 질문:</strong></p>
        <ul style="margin: 12px 0; padding-left: 20px;">
            <li>퇴직금은 어떻게 계산하나요?</li>
            <li>부당해고를 당했을 때 어떻게 해야 하나요?</li>
            <li>전세보증금을 돌려받지 못하면 어떻게 해야 하나요?</li>
            <li>온라인 쇼핑 환불 규정이 어떻게 되나요?</li>
        </ul>
        <p style="font-size: 0.85em; color: rgba(255,255,255,0.5); margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">
            ⚠️ 위 정보는 일반적인 법률 정보이며, 구체적인 사안은 변호사와 상담하시기 바랍니다.
        </p>
    `;
}

/* ===========================
   Mobile Menu Toggle
   =========================== */
const mobileToggle = document.querySelector('.nav-mobile-toggle');
const navLinks = document.querySelector('.nav-links');

if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
        mobileToggle.classList.toggle('active');
    });
}

/* ===========================
   Preloader
   =========================== */
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
    ScrollTrigger.refresh();

    // Re-initialize Lucide icons after page load
    lucide.createIcons();

    // Initialize count-up animation for trust values
    initCountUpAnimation();
});

/* ===========================
   Count-Up Animation for Stats
   =========================== */
function initCountUpAnimation() {
    const trustValues = document.querySelectorAll('.trust-value[data-count]');

    trustValues.forEach(el => {
        const target = parseInt(el.dataset.count, 10);
        const suffix = el.dataset.suffix || '';

        // ScrollTrigger로 화면에 보일 때 애니메이션 시작
        ScrollTrigger.create({
            trigger: el,
            start: 'top 85%',
            onEnter: () => {
                animateValue(el, 0, target, 2000, suffix);
            },
            once: true
        });
    });
}

function animateValue(el, start, end, duration, suffix) {
    el.classList.add('counting');
    const startTime = performance.now();
    const range = end - start;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // easeOutExpo 이징
        const easeProgress = 1 - Math.pow(2, -10 * progress);
        const current = Math.floor(start + range * easeProgress);

        // 숫자에 콤마 추가
        el.textContent = current.toLocaleString() + suffix;

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = end.toLocaleString() + suffix;
            el.classList.remove('counting');
        }
    }

    requestAnimationFrame(update);
}

/* ===========================
   Console Message
   =========================== */
console.log(
    '%c⚖️ LawBot',
    'font-size: 24px; font-weight: bold; color: #3b82f6;'
);
console.log(
    '%c4대 법률 분야 특화 AI 법률 정보 서비스',
    'font-size: 14px; color: #60a5fa;'
);
console.log(
    '%c본 서비스는 법률 정보 제공 목적이며, 법률 자문이 아닙니다.',
    'font-size: 12px; color: #888;'
);
