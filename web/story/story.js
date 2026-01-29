// Story Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    lucide.createIcons();

    // State
    let currentCategory = 'all';
    let displayedCount = 10;
    const ITEMS_PER_PAGE = 10;

    // DOM Elements
    const storiesGrid = document.getElementById('stories-grid');
    const loadMoreBtn = document.getElementById('load-more-btn');
    const filterTabs = document.querySelectorAll('.filter-tab');

    // Filter stories by category
    function filterStories(category) {
        if (category === 'all') {
            return storiesData;
        }
        return storiesData.filter(story => story.category === category);
    }

    // Create story card HTML
    function createStoryCard(story) {
        const card = document.createElement('div');
        card.className = 'story-card';
        card.dataset.id = story.id;

        card.innerHTML = `
            <div class="story-card-header">
                <span class="story-category ${story.category}">${story.categoryName}</span>
                <span class="story-date">${formatDate(story.date)}</span>
            </div>
            <h3 class="story-title">${story.title}</h3>
            <p class="story-excerpt">${story.excerpt}</p>
            <div class="story-meta">
                <span class="story-author">
                    <i data-lucide="user" class="icon-xs"></i>
                    ${story.author}
                </span>
                <div class="story-tags">
                    ${story.tags.slice(0, 2).map(tag => `<span class="story-tag">${tag}</span>`).join('')}
                </div>
            </div>
        `;

        // Add click event to open modal
        card.addEventListener('click', () => openModal(story));

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

    // Render stories
    function renderStories() {
        const filteredStories = filterStories(currentCategory);
        const storiesToShow = filteredStories.slice(0, displayedCount);

        storiesGrid.innerHTML = '';

        storiesToShow.forEach(story => {
            const card = createStoryCard(story);
            storiesGrid.appendChild(card);
        });

        // Reinitialize Lucide icons for new elements
        lucide.createIcons();

        // Update load more button
        if (displayedCount >= filteredStories.length) {
            loadMoreBtn.style.display = 'none';
        } else {
            loadMoreBtn.style.display = 'flex';
        }
    }

    // Handle filter tab click
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Update active state
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update current category and reset count
            currentCategory = tab.dataset.category;
            displayedCount = ITEMS_PER_PAGE;

            // Re-render stories
            renderStories();
        });
    });

    // Handle load more click
    loadMoreBtn.addEventListener('click', () => {
        displayedCount += ITEMS_PER_PAGE;
        renderStories();
    });

    // Modal functionality
    function openModal(story) {
        // Create modal if it doesn't exist
        let modal = document.querySelector('.story-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.className = 'story-modal';
            document.body.appendChild(modal);
        }

        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <button class="modal-close">
                    <i data-lucide="x" class="icon-sm"></i>
                </button>
                <div class="modal-header">
                    <span class="modal-category story-category ${story.category}">${story.categoryName}</span>
                    <h1 class="modal-title">${story.title}</h1>
                    <div class="modal-meta">
                        <span><i data-lucide="user" class="icon-xs"></i> ${story.author}</span>
                        <span><i data-lucide="calendar" class="icon-xs"></i> ${formatDate(story.date)}</span>
                    </div>
                </div>
                <div class="modal-body">
                    ${story.content.split('\n\n').map(p => `<p>${p}</p>`).join('')}

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
                        ${story.tags.map(tag => `<span class="modal-tag">#${tag}</span>`).join('')}
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
        const modal = document.querySelector('.story-modal');
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
    renderStories();
});
