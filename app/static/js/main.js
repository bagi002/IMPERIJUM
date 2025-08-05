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

// Show loading spinner with accessibility
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="spinner-border spinner-border-sm" role="status" aria-label="Loading"><span class="visually-hidden">Loading...</span></div>';
        element.setAttribute('aria-busy', 'true');
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.removeAttribute('aria-busy');
    }
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

// Enhanced notification system with accessibility
function showNotification(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.setAttribute('aria-live', 'polite');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close notification"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after specified duration
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }
    }, duration);
    
    // Announce to screen readers
    announceToScreenReader(`${type} notification: ${message}`);
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

// Export functions for global use
window.gameUtils = {
    formatCurrency,
    formatNumber,
    showNotification,
    confirmAction,
    updateGameData,
    refreshMarketData,
    announceToScreenReader,
    validateField
};