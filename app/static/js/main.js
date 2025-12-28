/* =====================================================
   RATING PREDICTOR - MAIN JAVASCRIPT
   Features: Toast, Dark Mode, Skeleton, Highlighting
===================================================== */

// ============ TOAST NOTIFICATION SYSTEM ============
class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }
    
    init() {
        // Create container if not exists
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }
    
    show(type, title, message, duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.setProperty('--toast-duration', `${duration}ms`);
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-times-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="toast-icon ${icons[type]}"></i>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        this.container.appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration + 300);
        
        return toast;
    }
    
    success(title, message, duration) {
        return this.show('success', title, message, duration);
    }
    
    error(title, message, duration) {
        return this.show('error', title, message, duration);
    }
    
    warning(title, message, duration) {
        return this.show('warning', title, message, duration);
    }
    
    info(title, message, duration) {
        return this.show('info', title, message, duration);
    }
}

// Global toast instance
const toast = new ToastManager();


// ============ DARK MODE MANAGER ============
class DarkModeManager {
    constructor() {
        this.isDark = false;
        this.init();
    }
    
    init() {
        // Check saved preference
        const savedMode = localStorage.getItem('darkMode');
        if (savedMode === 'true') {
            this.enable();
        } else if (savedMode === null) {
            // Check system preference
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                this.enable();
            }
        }
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (localStorage.getItem('darkMode') === null) {
                e.matches ? this.enable() : this.disable();
            }
        });
    }
    
    toggle() {
        this.isDark ? this.disable() : this.enable();
    }
    
    enable() {
        document.documentElement.classList.add('dark');
        this.isDark = true;
        localStorage.setItem('darkMode', 'true');
        this.updateCharts();
    }
    
    disable() {
        document.documentElement.classList.remove('dark');
        this.isDark = false;
        localStorage.setItem('darkMode', 'false');
        this.updateCharts();
    }
    
    updateCharts() {
        // Update Chart.js colors if charts exist
        if (typeof Chart !== 'undefined') {
            Chart.defaults.color = this.isDark ? '#94a3b8' : '#4b5563';
            Chart.defaults.borderColor = this.isDark ? '#334155' : '#e5e7eb';
        }
    }
}

// Global dark mode instance
const darkMode = new DarkModeManager();


// ============ LOADING SKELETON ============
class SkeletonLoader {
    static show(containerId, type = 'default') {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.setAttribute('data-original-content', container.innerHTML);
        
        let skeletonHtml = '';
        
        switch(type) {
            case 'table':
                skeletonHtml = `
                    <div class="skeleton-card">
                        ${Array(5).fill().map(() => `
                            <div class="flex items-center space-x-4 mb-4">
                                <div class="skeleton skeleton-text flex-1"></div>
                                <div class="skeleton skeleton-text" style="width: 60px;"></div>
                                <div class="skeleton skeleton-text" style="width: 80px;"></div>
                            </div>
                        `).join('')}
                    </div>
                `;
                break;
                
            case 'card':
                skeletonHtml = `
                    <div class="skeleton-card">
                        <div class="skeleton skeleton-title"></div>
                        <div class="skeleton skeleton-text"></div>
                        <div class="skeleton skeleton-text" style="width: 80%;"></div>
                        <div class="skeleton skeleton-text" style="width: 60%;"></div>
                    </div>
                `;
                break;
                
            case 'result':
                skeletonHtml = `
                    <div class="p-6 bg-gradient-to-r from-gray-100 to-gray-50 dark:from-gray-800 dark:to-gray-700 rounded-xl">
                        <div class="flex items-center space-x-6">
                            <div class="skeleton skeleton-circle" style="width: 80px; height: 80px;"></div>
                            <div class="flex-1">
                                <div class="skeleton skeleton-title"></div>
                                <div class="skeleton skeleton-text" style="width: 40%;"></div>
                            </div>
                        </div>
                    </div>
                `;
                break;
                
            case 'chart':
                skeletonHtml = `
                    <div class="skeleton-card">
                        <div class="skeleton skeleton-box" style="height: 200px;"></div>
                    </div>
                `;
                break;
                
            default:
                skeletonHtml = `
                    <div class="skeleton-card">
                        <div class="skeleton skeleton-text"></div>
                        <div class="skeleton skeleton-text" style="width: 80%;"></div>
                        <div class="skeleton skeleton-text" style="width: 60%;"></div>
                    </div>
                `;
        }
        
        container.innerHTML = skeletonHtml;
        container.classList.add('loading');
    }
    
    static hide(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const originalContent = container.getAttribute('data-original-content');
        if (originalContent) {
            container.innerHTML = originalContent;
            container.removeAttribute('data-original-content');
        }
        container.classList.remove('loading');
    }
    
    static showOverlay(message = 'Loading...') {
        // Remove existing overlay
        this.hideOverlay();
        
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'global-loading-overlay';
        overlay.innerHTML = `
            <div class="text-center text-white">
                <div class="loading-spinner mx-auto mb-4"></div>
                <p class="text-lg font-medium">${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    
    static hideOverlay() {
        const overlay = document.getElementById('global-loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
}


// ============ KEYWORD HIGHLIGHTING ============
class KeywordHighlighter {
    constructor() {
        // Vietnamese positive keywords
        this.positiveWords = [
            'tốt', 'đẹp', 'tuyệt vời', 'xuất sắc', 'hoàn hảo', 'chất lượng',
            'nhanh', 'tiện', 'ưng', 'hài lòng', 'thích', 'yêu', 'tuyệt',
            'ok', 'ổn', 'được', 'giỏi', 'hay', 'ngon', 'xịn', 'đỉnh',
            'pro', 'amazing', 'perfect', 'good', 'great', 'excellent',
            'rẻ', 'đáng tiền', 'đáng mua', 'recommend', 'khuyên', 'nên mua',
            'chính hãng', 'uy tín', 'nhiệt tình', 'chu đáo', 'cảm ơn',
            'giao nhanh', 'đóng gói cẩn thận', 'đúng mô tả', 'như hình'
        ];
        
        // Vietnamese negative keywords
        this.negativeWords = [
            'tệ', 'xấu', 'kém', 'dở', 'tồi', 'thất vọng', 'chán',
            'chậm', 'lâu', 'lỗi', 'hỏng', 'vỡ', 'rách', 'bẩn',
            'giả', 'fake', 'lừa', 'đắt', 'không đáng', 'phí tiền',
            'bad', 'poor', 'terrible', 'awful', 'worst', 'horrible',
            'không thích', 'không ưng', 'không hài lòng', 'không như',
            'trả lại', 'hoàn tiền', 'không đúng', 'sai', 'thiếu',
            'giao chậm', 'đóng gói ẩu', 'móp', 'méo', 'cũ'
        ];
    }
    
    highlight(text, additionalPositive = [], additionalNegative = []) {
        if (!text) return text;
        
        const allPositive = [...this.positiveWords, ...additionalPositive];
        const allNegative = [...this.negativeWords, ...additionalNegative];
        
        let highlightedText = text;
        
        // Sort by length (longer first) to avoid partial matches
        const sortByLength = (a, b) => b.length - a.length;
        
        // Highlight negative words first
        allNegative.sort(sortByLength).forEach(word => {
            const regex = new RegExp(`(${this.escapeRegex(word)})`, 'gi');
            highlightedText = highlightedText.replace(regex, '<span class="highlight-negative">$1</span>');
        });
        
        // Highlight positive words
        allPositive.sort(sortByLength).forEach(word => {
            const regex = new RegExp(`(${this.escapeRegex(word)})`, 'gi');
            highlightedText = highlightedText.replace(regex, '<span class="highlight-positive">$1</span>');
        });
        
        return highlightedText;
    }
    
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    // Highlight based on importance scores from SHAP/LIME
    highlightWithImportance(words, importanceScores) {
        return words.map((word, i) => {
            const score = importanceScores[i] || 0;
            if (score > 0.1) {
                return `<span class="highlight-positive">${word}</span>`;
            } else if (score < -0.1) {
                return `<span class="highlight-negative">${word}</span>`;
            }
            return word;
        }).join(' ');
    }
}

// Global highlighter instance
const highlighter = new KeywordHighlighter();


// ============ EXPLANATION VISUALIZER ============
class ExplanationVisualizer {
    static render(containerId, explanationData) {
        const container = document.getElementById(containerId);
        if (!container || !explanationData) return;
        
        const { words, importance_scores, overall_sentiment } = explanationData;
        
        // Sort by absolute importance
        const sortedItems = words.map((word, i) => ({
            word,
            score: importance_scores[i]
        })).sort((a, b) => Math.abs(b.score) - Math.abs(a.score));
        
        // Take top 10 most important words
        const topItems = sortedItems.slice(0, 10);
        
        // Find max absolute score for scaling
        const maxScore = Math.max(...topItems.map(item => Math.abs(item.score)));
        
        let html = `
            <div class="explanation-container fade-in">
                <h4 class="font-bold text-gray-800 dark:text-gray-200 mb-4">
                    <i class="fas fa-brain text-indigo-600 mr-2"></i>
                    Giải thích dự đoán (Top từ quan trọng)
                </h4>
                <div class="space-y-2">
        `;
        
        topItems.forEach(item => {
            const widthPercent = (Math.abs(item.score) / maxScore) * 100;
            const isPositive = item.score > 0;
            const colorClass = isPositive ? 'importance-positive' : 'importance-negative';
            const direction = isPositive ? 'right' : 'left';
            
            html += `
                <div class="importance-bar ${colorClass}" style="width: ${Math.max(widthPercent, 30)}%;">
                    <span class="font-medium">${item.word}</span>
                    <span>${item.score > 0 ? '+' : ''}${(item.score * 100).toFixed(1)}%</span>
                </div>
            `;
        });
        
        html += `
                </div>
                <div class="mt-4 text-sm text-gray-600 dark:text-gray-400">
                    <i class="fas fa-info-circle mr-1"></i>
                    Từ màu <span class="highlight-positive">xanh</span> đóng góp tích cực, 
                    từ màu <span class="highlight-negative">đỏ</span> đóng góp tiêu cực vào dự đoán.
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }
}


// ============ N-GRAM VISUALIZER ============
class NgramVisualizer {
    static render(containerId, ngramData, chartId = null) {
        const container = document.getElementById(containerId);
        if (!container || !ngramData) return;
        
        let html = '<div class="ngram-container">';
        
        // Display as badges
        ngramData.forEach(item => {
            html += `
                <div class="ngram-badge">
                    <span>${item.ngram}</span>
                    <span class="ngram-count">${item.count}</span>
                </div>
            `;
        });
        
        html += '</div>';
        
        container.innerHTML = html;
        
        // Render chart if chartId provided
        if (chartId) {
            this.renderChart(chartId, ngramData);
        }
    }
    
    static renderChart(chartId, ngramData) {
        const ctx = document.getElementById(chartId);
        if (!ctx) return;
        
        // Destroy existing chart
        const existingChart = Chart.getChart(ctx);
        if (existingChart) {
            existingChart.destroy();
        }
        
        const isDark = document.documentElement.classList.contains('dark');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ngramData.map(item => item.ngram),
                datasets: [{
                    label: 'Frequency',
                    data: ngramData.map(item => item.count),
                    backgroundColor: ngramData.map((_, i) => {
                        const hue = (i * 30) % 360;
                        return `hsla(${hue}, 70%, 60%, 0.8)`;
                    }),
                    borderColor: ngramData.map((_, i) => {
                        const hue = (i * 30) % 360;
                        return `hsla(${hue}, 70%, 50%, 1)`;
                    }),
                    borderWidth: 2
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: isDark ? '#334155' : '#e5e7eb'
                        },
                        ticks: {
                            color: isDark ? '#94a3b8' : '#4b5563'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: isDark ? '#94a3b8' : '#4b5563'
                        }
                    }
                }
            }
        });
    }
}


// ============ UTILITY FUNCTIONS ============
function formatConfidence(confidence) {
    return (confidence * 100).toFixed(1) + '%';
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString('vi-VN');
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for global use
window.toast = toast;
window.darkMode = darkMode;
window.SkeletonLoader = SkeletonLoader;
window.highlighter = highlighter;
window.ExplanationVisualizer = ExplanationVisualizer;
window.NgramVisualizer = NgramVisualizer;
