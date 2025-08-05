// IMPERIJUM Game JavaScript - Enhanced for accessibility and mobile

// Global game state
let gameState = {
    currentTurn: 1,
    playersReady: 0,
    totalPlayers: 0
};

// Accessibility and mobile optimization
document.addEventListener('DOMContentLoaded', function() {
    // Initialize core functionality
    initializeApp();
    
    // Auto-refresh game data every 10 seconds
    setInterval(updateGameData, 10000);
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize mobile optimizations
    initializeMobileOptimizations();
    
    // Initialize keyboard navigation
    initializeKeyboardNavigation();
    
    // Initialize accessibility features
    initializeAccessibility();
});

function initializeApp() {
    // Set up focus management
    setupFocusManagement();
    
    // Set up form enhancements
    setupFormEnhancements();
    
    // Set up mobile touch handlers
    setupTouchHandlers();
    
    // Add modern enhancements
    enhanceFormSubmission();
    addSmoothTransitions();
    
    // Initialize performance monitoring
    initializePerformanceMonitoring();
}

function initializeTooltips() {
    try {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    } catch (error) {
        console.log('Bootstrap tooltips not available');
    }
}

function initializeMobileOptimizations() {
    // Prevent zoom on form inputs for iOS
    if (navigator.userAgent.match(/iPhone|iPad|iPod/i)) {
        document.querySelectorAll('input, select, textarea').forEach(element => {
            if (!element.style.fontSize) {
                element.style.fontSize = '16px';
            }
        });
    }
    
    // Add touch feedback for buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('touchstart', function() {
            this.classList.add('active');
        });
        
        button.addEventListener('touchend', function() {
            setTimeout(() => {
                this.classList.remove('active');
            }, 150);
        });
    });
    
    // Optimize tables for mobile
    document.querySelectorAll('.table-responsive').forEach(table => {
        if (window.innerWidth < 768) {
            table.style.fontSize = '0.8rem';
        }
    });
}

function initializeKeyboardNavigation() {
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Alt + D = Dashboard
        if (e.altKey && e.key === 'd') {
            e.preventDefault();
            const dashboardLink = document.querySelector('a[href*="dashboard"]');
            if (dashboardLink) dashboardLink.click();
        }
        
        // Alt + C = Companies
        if (e.altKey && e.key === 'c') {
            e.preventDefault();
            const companiesLink = document.querySelector('a[href*="companies"]');
            if (companiesLink) companiesLink.click();
        }
        
        // Alt + M = Market
        if (e.altKey && e.key === 'm') {
            e.preventDefault();
            const marketLink = document.querySelector('a[href*="market"]');
            if (marketLink) marketLink.click();
        }
        
        // Escape key closes modals and dropdowns
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(modal => {
                bootstrap.Modal.getInstance(modal)?.hide();
            });
            document.querySelectorAll('.dropdown-menu.show').forEach(dropdown => {
                bootstrap.Dropdown.getInstance(dropdown.previousElementSibling)?.hide();
            });
        }
    });
}

function initializeAccessibility() {
    // Announce page changes to screen readers
    const announceEl = document.createElement('div');
    announceEl.setAttribute('aria-live', 'polite');
    announceEl.setAttribute('aria-atomic', 'true');
    announceEl.className = 'sr-only';
    announceEl.id = 'aria-announcements';
    document.body.appendChild(announceEl);
    
    // Add skip links functionality
    const skipLink = document.querySelector('a[href="#main-content"]');
    if (skipLink) {
        skipLink.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.getElementById('main-content');
            if (target) {
                target.focus();
                target.scrollIntoView();
            }
        });
    }
}

function setupFocusManagement() {
    // Trap focus in modals
    document.addEventListener('shown.bs.modal', function(e) {
        const modal = e.target;
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    });
}

function setupFormEnhancements() {
    // Add loading states to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Loading...';
            }
        });
    });
    
    // Add real-time validation feedback
    document.querySelectorAll('input[required], textarea[required], select[required]').forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
}

function setupTouchHandlers() {
    // Add touch-friendly swipe gestures for tables
    let startX, startY;
    
    document.querySelectorAll('.table-responsive').forEach(table => {
        table.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        table.addEventListener('touchmove', function(e) {
            if (!startX || !startY) return;
            
            const diffX = startX - e.touches[0].clientX;
            const diffY = startY - e.touches[0].clientY;
            
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 10) {
                e.preventDefault(); // Prevent vertical scroll while swiping horizontally
            }
        });
    });
}

function validateField(field) {
    const errorElement = field.parentNode.querySelector('.field-error');
    
    if (!field.value && field.required) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    if (field.type === 'email' && field.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    clearFieldError(field);
    return true;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error text-danger small mt-1';
    errorElement.textContent = message;
    errorElement.setAttribute('role', 'alert');
    
    field.classList.add('is-invalid');
    field.parentNode.appendChild(errorElement);
}

function clearFieldError(field) {
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.remove();
    }
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
}

// Update game data from API
function updateGameData() {
    fetch('/api/game_state')
        .then(response => response.json())
        .then(data => {
            gameState = data;
            updateGameStateDisplay();
            announceToScreenReader(`Game state updated. Turn ${data.currentTurn}`);
        })
        .catch(error => {
            console.error('Error fetching game state:', error);
        });
}

// Update game state display elements
function updateGameStateDisplay() {
    // Update turn indicator
    const turnBadges = document.querySelectorAll('.turn-badge');
    turnBadges.forEach(badge => {
        badge.textContent = `Turn ${gameState.currentTurn}`;
        badge.setAttribute('aria-label', `Current turn: ${gameState.currentTurn}`);
    });
    
    // Update players ready progress
    const progressBars = document.querySelectorAll('.players-progress');
    progressBars.forEach(bar => {
        const percentage = gameState.totalPlayers > 0 ? 
            (gameState.playersReady / gameState.totalPlayers) * 100 : 0;
        bar.style.width = `${percentage}%`;
        bar.setAttribute('aria-valuenow', gameState.playersReady);
        bar.setAttribute('aria-valuemax', gameState.totalPlayers);
        bar.setAttribute('aria-label', `${gameState.playersReady} of ${gameState.totalPlayers} players ready`);
    });
}

// Accessibility announcement function
function announceToScreenReader(message) {
    const announceEl = document.getElementById('aria-announcements');
    if (announceEl) {
        announceEl.textContent = message;
        setTimeout(() => {
            announceEl.textContent = '';
        }, 1000);
    }
}

// Format currency values
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(amount);
}

// Format large numbers
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Modern loading spinner with better UX
function showModernLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="d-flex flex-column align-items-center justify-content-center py-4">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="text-muted mb-0">${message}</p>
            </div>
        `;
        element.setAttribute('aria-busy', 'true');
        element.style.opacity = '0.8';
    }
}

function hideModernLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.removeAttribute('aria-busy');
        element.style.opacity = '1';
    }
}

// Enhanced form submission with loading states
function enhanceFormSubmission() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                const originalText = submitButton.innerHTML;
                submitButton.disabled = true;
                submitButton.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Processing...
                `;
                
                // Re-enable button after 5 seconds as fallback
                setTimeout(() => {
                    if (submitButton.disabled) {
                        submitButton.disabled = false;
                        submitButton.innerHTML = originalText;
                    }
                }, 5000);
            }
        });
    });
}

// Smooth transitions for page elements
function addSmoothTransitions() {
    document.querySelectorAll('.card, .btn, .alert').forEach(element => {
        element.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    });
}

// Modern data refresh with visual feedback
function refreshWithFeedback(url, containerId, successMessage = 'Data updated successfully') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Add loading state
    showModernLoading(containerId, 'Fetching latest data...');
    
    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideModernLoading(containerId);
            showNotification(successMessage, 'success', 3000);
            return data;
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            container.innerHTML = `
                <div class="text-center py-4">
                    <div class="mb-3">
                        <span style="font-size: 3rem; opacity: 0.3;">⚠️</span>
                    </div>
                    <h6 class="text-muted">Unable to load data</h6>
                    <p class="text-muted mb-3">Please check your connection and try again</p>
                    <button class="btn btn-outline-primary btn-sm" onclick="refreshWithFeedback('${url}', '${containerId}')">
                        🔄 Retry
                    </button>
                </div>
            `;
            showNotification('Failed to load data. Please try again.', 'error', 4000);
            hideModernLoading(containerId);
            throw error;
        });
}

// Market data refresh with better error handling
function refreshMarketData() {
    showLoading('market-data');
    
    fetch('/api/market_data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            updateMarketDisplay(data);
            hideLoading('market-data');
            announceToScreenReader('Market data updated');
        })
        .catch(error => {
            console.error('Error fetching market data:', error);
            const container = document.getElementById('market-data');
            if (container) {
                container.innerHTML = '<div class="alert alert-danger" role="alert">Error loading market data. Please try again.</div>';
            }
            hideLoading('market-data');
        });
}

// Update market display with accessibility
function updateMarketDisplay(marketData) {
    const container = document.getElementById('market-data');
    if (!container) return;
    
    let html = '<div class="row">';
    
    marketData.forEach((product, index) => {
        if (index < 6) { // Show only first 6 products
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card" role="article" aria-label="Product: ${product.name}">
                        <div class="card-body p-2">
                            <h6 class="card-title mb-1">${product.name}</h6>
                            <p class="card-text mb-1">
                                <small class="text-muted">${product.category}</small><br>
                                <strong aria-label="Price: ${formatCurrency(product.market_price)}">${formatCurrency(product.market_price)}</strong>
                            </p>
                            <small class="text-muted" aria-label="Stock quantity: ${product.stock_quantity}">Stock: ${product.stock_quantity}</small>
                        </div>
                    </div>
                </div>
            `;
        }
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Enhanced notification system with modern toasts
function showNotification(message, type = 'info', duration = 5000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const iconMap = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast show`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="toast-header bg-${type} text-white">
            <span class="me-2">${iconMap[type] || 'ℹ️'}</span>
            <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-dismiss after specified duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }
    }, duration);
    
    // Announce to screen readers
    announceToScreenReader(`${type} notification: ${message}`);
    
    return toast;
}

// Accessible confirm dialog
function confirmAction(message, callback) {
    // In a real implementation, this could use a custom modal for better accessibility
    if (confirm(message)) {
        callback();
    }
}

// Enhanced charts initialization
function initializeCharts() {
    const marketChartCanvas = document.getElementById('marketChart');
    if (marketChartCanvas && typeof Chart !== 'undefined') {
        fetch('/api/market_data')
            .then(response => response.json())
            .then(data => {
                const ctx = marketChartCanvas.getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.map(p => p.name),
                        datasets: [{
                            label: 'Market Price',
                            data: data.map(p => p.market_price),
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        interaction: {
                            intersect: false,
                        },
                        plugins: {
                            legend: {
                                labels: {
                                    usePointStyle: true,
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`;
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: false,
                                ticks: {
                                    callback: function(value) {
                                        return formatCurrency(value);
                                    }
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error loading chart data:', error);
                marketChartCanvas.parentNode.innerHTML = '<p class="text-muted">Chart unavailable</p>';
            });
    }
}

// Window resize handler for responsive adjustments
window.addEventListener('resize', function() {
    // Recalculate mobile optimizations
    if (window.innerWidth < 768) {
        document.querySelectorAll('.table-responsive').forEach(table => {
            table.style.fontSize = '0.8rem';
        });
    } else {
        document.querySelectorAll('.table-responsive').forEach(table => {
            table.style.fontSize = '';
        });
    }
});

// Performance monitoring for better UX
function initializePerformanceMonitoring() {
    // Monitor page load performance
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
        
        // Show performance notification for slow loads
        if (loadTime > 3000) {
            showNotification('Page loaded slowly. Consider refreshing if you experience issues.', 'warning', 6000);
        }
    });
    
    // Monitor API call performance
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const startTime = performance.now();
        return originalFetch.apply(this, args)
            .then(response => {
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                if (duration > 2000) {
                    console.warn(`Slow API call detected: ${args[0]} took ${duration.toFixed(2)}ms`);
                }
                
                return response;
            });
    };
}

// Modern confirmation dialogs
function modernConfirm(title, message, confirmText = 'Confirm', cancelText = 'Cancel') {
    return new Promise((resolve) => {
        // Create modal HTML
        const modalHtml = `
            <div class="modal fade" id="confirmModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header border-0">
                            <h5 class="modal-title fw-bold">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p class="mb-0">${message}</p>
                        </div>
                        <div class="modal-footer border-0">
                            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">${cancelText}</button>
                            <button type="button" class="btn btn-primary" id="confirmBtn">${confirmText}</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('confirmModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
        
        // Handle confirmation
        document.getElementById('confirmBtn').addEventListener('click', function() {
            modal.hide();
            resolve(true);
        });
        
        // Handle cancellation
        document.getElementById('confirmModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
            resolve(false);
        });
        
        modal.show();
    });
}

// Export enhanced functions for global use
window.gameUtils = {
    formatCurrency,
    formatNumber,
    showNotification,
    confirmAction: modernConfirm,
    updateGameData,
    refreshMarketData,
    announceToScreenReader,
    validateField,
    showModernLoading,
    hideModernLoading,
    refreshWithFeedback
};