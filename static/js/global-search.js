/**
 * Global Search System for Asetena Management System
 * Provides instant search across students, teachers, classes, and subjects
 * Keyboard shortcut: Ctrl+K or Cmd+K
 */

class GlobalSearch {
    constructor() {
        this.searchModal = null;
        this.searchInput = null;
        this.resultsContainer = null;
        this.isOpen = false;
        this.searchTimeout = null;
        this.selectedIndex = -1;
        this.results = [];
        
        this.init();
    }

    init() {
        this.createSearchModal();
        this.attachEventListeners();
        this.setupKeyboardShortcut();
    }

    createSearchModal() {
        // Create modal HTML
        const modalHTML = `
            <div class="modal fade" id="globalSearchModal" tabindex="-1" aria-labelledby="globalSearchLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content border-0 shadow-lg">
                        <div class="modal-header border-0 pb-0">
                            <div class="search-input-wrapper w-100">
                                <i class="bi bi-search search-icon"></i>
                                <input type="text" 
                                       class="form-control form-control-lg border-0 shadow-none ps-5" 
                                       id="globalSearchInput" 
                                       placeholder="Search students, teachers, classes, subjects... (Ctrl+K)"
                                       autocomplete="off">
                                <button type="button" class="btn-close search-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                        </div>
                        <div class="modal-body pt-2">
                            <div id="searchResults" class="search-results">
                                <div class="search-hints text-center py-4">
                                    <i class="bi bi-search fs-1 text-muted mb-3 d-block"></i>
                                    <p class="text-muted mb-2">Start typing to search across the system</p>
                                    <div class="search-tips">
                                        <span class="badge bg-light text-dark me-2"><i class="bi bi-person"></i> Students</span>
                                        <span class="badge bg-light text-dark me-2"><i class="bi bi-person-badge"></i> Teachers</span>
                                        <span class="badge bg-light text-dark me-2"><i class="bi bi-book"></i> Classes</span>
                                        <span class="badge bg-light text-dark"><i class="bi bi-journal"></i> Subjects</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer border-0 pt-0">
                            <div class="search-shortcuts w-100 d-flex justify-content-between">
                                <small class="text-muted">
                                    <kbd>↑</kbd> <kbd>↓</kbd> Navigate
                                </small>
                                <small class="text-muted">
                                    <kbd>Enter</kbd> Select
                                </small>
                                <small class="text-muted">
                                    <kbd>Esc</kbd> Close
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Append to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Get references
        this.searchModal = new bootstrap.Modal(document.getElementById('globalSearchModal'));
        this.searchInput = document.getElementById('globalSearchInput');
        this.resultsContainer = document.getElementById('searchResults');
    }

    attachEventListeners() {
        // Search input
        this.searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            // Clear previous timeout
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }

            // Debounce search
            this.searchTimeout = setTimeout(() => {
                if (query.length >= 2) {
                    this.performSearch(query);
                } else {
                    this.showHints();
                }
            }, 300);
        });

        // Keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateResults('down');
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateResults('up');
            } else if (e.key === 'Enter') {
                e.preventDefault();
                this.selectResult();
            }
        });

        // Reset on modal close
        document.getElementById('globalSearchModal').addEventListener('hidden.bs.modal', () => {
            this.searchInput.value = '';
            this.showHints();
            this.selectedIndex = -1;
            this.isOpen = false;
        });

        // Focus input when modal opens
        document.getElementById('globalSearchModal').addEventListener('shown.bs.modal', () => {
            this.searchInput.focus();
            this.isOpen = true;
        });
    }

    setupKeyboardShortcut() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+K or Cmd+K
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.open();
            }
        });
    }

    open() {
        this.searchModal.show();
    }

    close() {
        this.searchModal.hide();
    }

    showHints() {
        this.resultsContainer.innerHTML = `
            <div class="search-hints text-center py-4">
                <i class="bi bi-search fs-1 text-muted mb-3 d-block"></i>
                <p class="text-muted mb-2">Start typing to search across the system</p>
                <div class="search-tips">
                    <span class="badge bg-light text-dark me-2"><i class="bi bi-person"></i> Students</span>
                    <span class="badge bg-light text-dark me-2"><i class="bi bi-person-badge"></i> Teachers</span>
                    <span class="badge bg-light text-dark me-2"><i class="bi bi-book"></i> Classes</span>
                    <span class="badge bg-light text-dark"><i class="bi bi-journal"></i> Subjects</span>
                </div>
            </div>
        `;
    }

    showLoading() {
        this.resultsContainer.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="text-muted mt-2">Searching...</p>
            </div>
        `;
    }

    async performSearch(query) {
        this.showLoading();

        try {
            const response = await fetch(`/api/global-search/?q=${encodeURIComponent(query)}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            if (!response.ok) {
                throw new Error('Search request failed');
            }

            const data = await response.json();
            this.results = data.results || [];
            this.displayResults(query);
        } catch (error) {
            console.error('Search error:', error);
            this.showError();
        }
    }

    displayResults(query) {
        if (this.results.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-inbox fs-1 text-muted mb-3 d-block"></i>
                    <p class="text-muted">No results found for "${this.escapeHtml(query)}"</p>
                </div>
            `;
            return;
        }

        // Group results by type
        const grouped = this.groupResultsByType(this.results);
        
        let html = '';
        
        for (const [type, items] of Object.entries(grouped)) {
            if (items.length === 0) continue;
            
            html += `
                <div class="result-group">
                    <div class="result-group-header">
                        <i class="bi ${this.getTypeIcon(type)}"></i>
                        ${type.charAt(0).toUpperCase() + type.slice(1)}
                        <span class="badge bg-secondary ms-2">${items.length}</span>
                    </div>
                    <div class="result-items">
            `;
            
            items.forEach((item, index) => {
                const globalIndex = this.results.indexOf(item);
                html += this.renderResultItem(item, globalIndex);
            });
            
            html += `
                    </div>
                </div>
            `;
        }

        this.resultsContainer.innerHTML = html;
        this.attachResultListeners();
    }

    renderResultItem(item, index) {
        const isSelected = index === this.selectedIndex ? 'selected' : '';
        
        return `
            <div class="result-item ${isSelected}" data-index="${index}" data-url="${item.url}">
                <div class="result-icon">
                    <i class="bi ${this.getTypeIcon(item.type)}"></i>
                </div>
                <div class="result-content">
                    <div class="result-title">${this.escapeHtml(item.title)}</div>
                    <div class="result-subtitle">${this.escapeHtml(item.subtitle || '')}</div>
                </div>
                <div class="result-actions">
                    ${this.renderQuickActions(item)}
                    <i class="bi bi-arrow-right-short ms-2"></i>
                </div>
            </div>
        `;
    }

    renderQuickActions(item) {
        let actions = '';
        
        if (item.type === 'students') {
            actions = `
                <button class="btn btn-sm btn-outline-primary me-1" onclick="event.stopPropagation(); window.location='${item.grades_url}'">
                    <i class="bi bi-card-checklist"></i>
                </button>
                <button class="btn btn-sm btn-outline-success me-1" onclick="event.stopPropagation(); window.location='${item.attendance_url}'">
                    <i class="bi bi-calendar-check"></i>
                </button>
            `;
        } else if (item.type === 'teachers') {
            actions = `
                <button class="btn btn-sm btn-outline-primary me-1" onclick="event.stopPropagation(); window.location='${item.schedule_url}'">
                    <i class="bi bi-calendar"></i>
                </button>
            `;
        } else if (item.type === 'classes') {
            actions = `
                <button class="btn btn-sm btn-outline-primary me-1" onclick="event.stopPropagation(); window.location='${item.students_url}'">
                    <i class="bi bi-people"></i>
                </button>
            `;
        }
        
        return actions;
    }

    attachResultListeners() {
        const items = this.resultsContainer.querySelectorAll('.result-item');
        items.forEach(item => {
            item.addEventListener('click', () => {
                const url = item.dataset.url;
                if (url) {
                    window.location.href = url;
                }
            });

            item.addEventListener('mouseenter', () => {
                this.selectedIndex = parseInt(item.dataset.index);
                this.updateSelection();
            });
        });
    }

    navigateResults(direction) {
        if (this.results.length === 0) return;

        if (direction === 'down') {
            this.selectedIndex = Math.min(this.selectedIndex + 1, this.results.length - 1);
        } else {
            this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
        }

        this.updateSelection();
        this.scrollToSelected();
    }

    updateSelection() {
        const items = this.resultsContainer.querySelectorAll('.result-item');
        items.forEach((item, index) => {
            if (parseInt(item.dataset.index) === this.selectedIndex) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    scrollToSelected() {
        const selectedItem = this.resultsContainer.querySelector('.result-item.selected');
        if (selectedItem) {
            selectedItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    selectResult() {
        if (this.selectedIndex >= 0 && this.results[this.selectedIndex]) {
            const result = this.results[this.selectedIndex];
            if (result.url) {
                window.location.href = result.url;
            }
        }
    }

    groupResultsByType(results) {
        const grouped = {
            students: [],
            teachers: [],
            classes: [],
            subjects: []
        };

        results.forEach(item => {
            if (grouped[item.type]) {
                grouped[item.type].push(item);
            }
        });

        return grouped;
    }

    getTypeIcon(type) {
        const icons = {
            students: 'bi-person',
            teachers: 'bi-person-badge',
            classes: 'bi-book',
            subjects: 'bi-journal'
        };
        return icons[type] || 'bi-search';
    }

    showError() {
        this.resultsContainer.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-exclamation-triangle fs-1 text-danger mb-3 d-block"></i>
                <p class="text-muted">An error occurred while searching. Please try again.</p>
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize global search when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.globalSearch = new GlobalSearch();
    
    // Add search button to navbar if it doesn't exist
    const navbar = document.querySelector('.navbar');
    if (navbar && !document.querySelector('.global-search-trigger')) {
        const searchButton = document.createElement('button');
        searchButton.className = 'btn btn-outline-light me-2 global-search-trigger';
        searchButton.innerHTML = '<i class="bi bi-search me-1"></i> Search <kbd class="ms-1">Ctrl+K</kbd>';
        searchButton.onclick = () => window.globalSearch.open();
        
        const navbarNav = navbar.querySelector('.navbar-nav');
        if (navbarNav) {
            navbarNav.parentElement.insertBefore(searchButton, navbarNav);
        }
    }
});
