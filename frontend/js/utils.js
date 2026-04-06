// Utility Functions for Toonify AI

// Toast notification function
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.className = `toast px-6 py-4 rounded-xl shadow-2xl backdrop-blur-xl border z-50 ${type === 'success' ? 'bg-green-500/90 border-green-400 text-white' :
            type === 'error' ? 'bg-red-500/90 border-red-400 text-white' :
                type === 'warning' ? 'bg-yellow-500/90 border-yellow-400 text-white' :
                    'bg-blue-500/90 border-blue-400 text-white'
        }`;

    // Add icon
    const icon = type === 'success' ? '✅' :
        type === 'error' ? '❌' :
            type === 'warning' ? '⚠️' : 'ℹ️';

    toast.innerHTML = `
        <div class="flex items-center gap-3">
            <span class="text-xl">${icon}</span>
            <span>${message}</span>
        </div>
    `;

    container.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// File validation
function validateFile(file, maxSizeMB = 10, allowedTypes = ['image/jpeg', 'image/png', 'image/webp']) {
    if (!file) {
        return { valid: false, error: 'No file selected' };
    }

    // Check file type
    if (!allowedTypes.includes(file.type)) {
        return {
            valid: false,
            error: `Invalid file type. Allowed types: ${allowedTypes.map(t => t.split('/')[1].toUpperCase()).join(', ')}`
        };
    }

    // Check file size
    const maxSize = maxSizeMB * 1024 * 1024;
    if (file.size > maxSize) {
        return {
            valid: false,
            error: `File too large. Maximum size: ${maxSizeMB}MB`
        };
    }

    return { valid: true };
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    // Less than 1 minute
    if (diff < 60000) {
        return 'Just now';
    }

    // Less than 1 hour
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    }

    // Less than 1 day
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }

    // Less than 1 week
    if (diff < 604800000) {
        const days = Math.floor(diff / 86400000);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }

    // Format as date
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Debounce function
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

// Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!', 'success');
    } catch (error) {
        console.error('Failed to copy:', error);
        showToast('Failed to copy to clipboard', 'error');
    }
}

// Generate random ID
function generateId() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

// Get status badge HTML
function getStatusBadge(status) {
    const badges = {
        'completed': '<span class="inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full text-xs font-semibold"><span class="w-2 h-2 bg-white rounded-full"></span>COMPLETED</span>',
        'processing': '<span class="inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full text-xs font-semibold"><svg class="w-3 h-3 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>PROCESSING</span>',
        'failed': '<span class="inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-red-500 to-pink-500 rounded-full text-xs font-semibold"><span class="w-2 h-2 bg-white rounded-full"></span>FAILED</span>',
        'pending': '<span class="inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full text-xs font-semibold"><span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>PENDING</span>',
    };

    return badges[status] || badges['pending'];
}

// Get style icon
function getStyleIcon(style) {
    const icons = {
        'cartoon': '🎬',
        'pencil': '✏️',
        'color_pencil': '🖍️',
        'edge': '🔲',
        'watercolor': '💧',
        'anime': '🎌',
        'oil': '🎨',
    };

    return icons[style] || '🎨';
}

// Get style name
function getStyleName(style) {
    const names = {
        'cartoon': 'Cartoon Style',
        'pencil': 'Pencil Sketch',
        'color_pencil': 'Color Pencil',
        'edge': 'Edge Preserve',
        'watercolor': 'Watercolor',
        'anime': 'Anime Style',
        'oil': 'Oil Painting',
    };

    return names[style] || style;
}

// Create loading skeleton
function createSkeleton(height = '64') {
    return `
        <div class="animate-pulse space-y-4">
            <div class="h-4 bg-white/10 rounded w-3/4"></div>
            <div class="h-4 bg-white/10 rounded w-1/2"></div>
            <div class="h-${height} bg-white/10 rounded-2xl"></div>
        </div>
    `;
}

// Create spinner
function createSpinner(size = 'w-8 h-8') {
    return `
        <svg class="animate-spin ${size} text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
    `;
}

// Image preview helper
function previewImage(file, imgElement) {
    const reader = new FileReader();

    reader.onload = function (e) {
        imgElement.src = e.target.result;
    };

    reader.onerror = function () {
        showToast('Failed to read file', 'error');
    };

    reader.readAsDataURL(file);
}

// Truncate text
function truncate(text, maxLength = 50) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Get confidence color
function getConfidenceColor(confidence) {
    if (confidence >= 80) return 'from-green-500 to-emerald-500';
    if (confidence >= 50) return 'from-blue-500 to-cyan-500';
    return 'from-purple-500 to-pink-500';
}

// Format percentage
function formatPercentage(value) {
    return (value * 100).toFixed(1) + '%';
}

// Create progress bar
function createProgressBar(percentage, label = '') {
    const color = getConfidenceColor(percentage);

    return `
        <div class="space-y-2">
            ${label ? `
                <div class="flex justify-between text-sm">
                    <span class="text-gray-400">${label}</span>
                    <span class="font-semibold bg-gradient-to-r ${color} bg-clip-text text-transparent">${formatPercentage(percentage / 100)}</span>
                </div>
            ` : ''}
            <div class="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r ${color} rounded-full transition-all duration-1000 ease-out" style="width: ${percentage}%"></div>
            </div>
        </div>
    `;
}

// Local storage helpers
const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Storage error:', error);
        }
    },

    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Storage error:', error);
            return defaultValue;
        }
    },

    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Storage error:', error);
        }
    },

    clear: () => {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Storage error:', error);
        }
    },
};

// Export utilities
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showToast,
        validateFile,
        formatFileSize,
        formatDate,
        debounce,
        copyToClipboard,
        generateId,
        getStatusBadge,
        getStyleIcon,
        getStyleName,
        createSkeleton,
        createSpinner,
        previewImage,
        truncate,
        getConfidenceColor,
        formatPercentage,
        createProgressBar,
        storage,
    };
}
