// Blog Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    lucide.createIcons();

    // State
    let currentCategory = 'all';

    // DOM Elements
    const blogGrid = document.getElementById('blog-grid');
    const filterTabs = document.querySelectorAll('.filter-tab');

    // Filter blogs by category
    function filterBlogs(category) {
        if (category === 'all') {
            return blogData;
        }
        return blogData.filter(blog => blog.category === category);
    }

    // Create blog card HTML
    function createBlogCard(blog) {
        const card = document.createElement('article');
        card.className = 'blog-card';
        card.dataset.category = blog.category;
        card.dataset.id = blog.id;

        card.innerHTML = `
            <div class="blog-card-link">
                <div class="blog-card-header">
                    <span class="blog-badge ${blog.category}">${blog.categoryName}</span>
                    <span class="blog-date">${formatDate(blog.date)}</span>
                </div>
                <h2 class="blog-card-title">${blog.title}</h2>
                <p class="blog-card-desc">${blog.excerpt}</p>
                <div class="blog-card-footer">
                    <span class="read-time"><i data-lucide="clock" class="icon-xs"></i> ${blog.readTime}분 읽기</span>
                </div>
            </div>
        `;

        // Add click event to open modal
        card.addEventListener('click', () => openModal(blog));

        return card;
    }

    // Format date
    function formatDate(dateStr) {
        const date = new Date(dateStr);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}.${month}.${day}`;
    }

    // Render blogs
    function renderBlogs() {
        const filteredBlogs = filterBlogs(currentCategory);

        blogGrid.innerHTML = '';

        filteredBlogs.forEach(blog => {
            const card = createBlogCard(blog);
            blogGrid.appendChild(card);
        });

        // Reinitialize Lucide icons for new elements
        lucide.createIcons();
    }

    // Handle filter tab click
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Update active state
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update current category
            currentCategory = tab.dataset.category;

            // Re-render blogs
            renderBlogs();
        });
    });

    // Parse markdown-like content to HTML (상세 페이지 스타일)
    function parseContent(content, category) {
        return content.split('\n\n').map(p => {
            // **제목** 형태로 시작하고 끝나면 h2
            if (p.startsWith('**') && p.endsWith('**')) {
                return `<h2>${p.replace(/\*\*/g, '')}</h2>`;
            }
            // **제목** 형태로 시작하면 h3
            else if (p.startsWith('**')) {
                const title = p.match(/^\*\*([^*]+)\*\*/);
                if (title) {
                    const rest = p.replace(/^\*\*[^*]+\*\*\s*/, '');
                    if (rest) {
                        return `<h3>${title[1]}</h3><p>${rest.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')}</p>`;
                    }
                    return `<h3>${title[1]}</h3>`;
                }
            }
            // 리스트 (- 또는 □로 시작)
            else if (p.startsWith('-') || p.startsWith('□')) {
                const items = p.split('\n').map(item =>
                    `<li>${item.replace(/^[-□]\s*/, '').replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')}</li>`
                ).join('');
                return `<ul>${items}</ul>`;
            }
            // 숫자 리스트
            else if (p.match(/^\d+[\.\)]/)) {
                const items = p.split('\n').map(item =>
                    `<li>${item.replace(/^\d+[\.\)]\s*/, '').replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')}</li>`
                ).join('');
                return `<ol>${items}</ol>`;
            }
            // 일반 문단
            else {
                return `<p>${p.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')}</p>`;
            }
        }).join('');
    }

    // Modal functionality
    function openModal(blog) {
        // Create modal if it doesn't exist
        let modal = document.querySelector('.blog-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.className = 'blog-modal';
            document.body.appendChild(modal);
        }

        const parsedContent = parseContent(blog.content, blog.category);

        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <button class="modal-close">
                    <i data-lucide="x" class="icon-sm"></i>
                </button>
                <div class="modal-header">
                    <span class="modal-category blog-badge ${blog.category}">${blog.categoryName}</span>
                    <h1 class="modal-title">${blog.title}</h1>
                    <div class="modal-meta">
                        <span><i data-lucide="calendar" class="icon-xs"></i> ${formatDate(blog.date)}</span>
                        <span><i data-lucide="clock" class="icon-xs"></i> ${blog.readTime}분 읽기</span>
                    </div>
                </div>
                <div class="modal-body">
                    ${parsedContent}

                    <div class="post-disclaimer">
                        <div class="post-disclaimer-title"><i data-lucide="alert-circle" class="icon-sm"></i> 법률 정보 안내</div>
                        <p>이 글은 일반적인 법률 정보를 제공하기 위한 것으로, 구체적인 법률 자문이 아닙니다. 개별 사안에 따라 결과가 달라질 수 있으므로, 정확한 판단을 위해서는 변호사와 상담하시기 바랍니다.</p>
                    </div>

                    <div class="post-cta">
                        <h3>비슷한 상황이신가요?</h3>
                        <p>AI 법률 상담으로 더 자세한 정보를 확인해보세요.</p>
                        <div class="post-cta-buttons">
                            <a href="../index.html#hero" class="post-cta-btn primary">
                                <i data-lucide="message-circle" class="icon-sm"></i>
                                AI 상담 시작하기
                            </a>
                            <a href="../contact.html" class="post-cta-btn secondary">
                                <i data-lucide="user" class="icon-sm"></i>
                                변호사 상담 신청
                            </a>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <div class="modal-tags">
                        ${blog.tags.map(tag => `<span class="modal-tag">#${tag}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;

        modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Reinitialize icons
        lucide.createIcons();

        // Close modal handlers
        const closeBtn = modal.querySelector('.modal-close');
        const backdrop = modal.querySelector('.modal-backdrop');

        closeBtn.addEventListener('click', closeModal);
        backdrop.addEventListener('click', closeModal);

        // Close on escape key
        document.addEventListener('keydown', handleEscKey);
    }

    function closeModal() {
        const modal = document.querySelector('.blog-modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            document.removeEventListener('keydown', handleEscKey);
        }
    }

    function handleEscKey(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
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

            // 메뉴 열릴 때 body 스크롤 방지
            if (isOpening) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });

        // Close menu when clicking a link
        navLinks.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                mobileToggle.classList.remove('active');
                navLinks.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }

    // Initial render
    renderBlogs();
});
