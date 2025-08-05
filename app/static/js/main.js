// IMPERIJUM Game JavaScript

// Global game state
let gameState = {
    currentTurn: 1,
    playersReady: 0,
    totalPlayers: 0
};

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh game data every 10 seconds
    setInterval(updateGameData, 10000);
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Update game data from API
function updateGameData() {
    fetch('/api/game_state')
        .then(response => response.json())
        .then(data => {
            gameState = data;
            updateGameStateDisplay();
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
    });
    
    // Update players ready progress
    const progressBars = document.querySelectorAll('.players-progress');
    progressBars.forEach(bar => {
        const percentage = gameState.totalPlayers > 0 ? 
            (gameState.playersReady / gameState.totalPlayers) * 100 : 0;
        bar.style.width = `${percentage}%`;
        bar.setAttribute('aria-valuenow', gameState.playersReady);
    });
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

// Show loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>';
    }
}

// Market data refresh
function refreshMarketData() {
    showLoading('market-data');
    
    fetch('/api/market_data')
        .then(response => response.json())
        .then(data => {
            updateMarketDisplay(data);
        })
        .catch(error => {
            console.error('Error fetching market data:', error);
            document.getElementById('market-data').innerHTML = '<p class="text-danger">Error loading market data</p>';
        });
}

// Update market display
function updateMarketDisplay(marketData) {
    const container = document.getElementById('market-data');
    if (!container) return;
    
    let html = '<div class="row">';
    
    marketData.forEach((product, index) => {
        if (index < 6) { // Show only first 6 products
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body p-2">
                            <h6 class="card-title mb-1">${product.name}</h6>
                            <p class="card-text mb-1">
                                <small class="text-muted">${product.category}</small><br>
                                <strong>${formatCurrency(product.market_price)}</strong>
                            </p>
                            <small class="text-muted">Stock: ${product.stock_quantity}</small>
                        </div>
                    </div>
                </div>
            `;
        }
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Company management functions
function buyStock(companyId, shares) {
    const form = new FormData();
    form.append('company_id', companyId);
    form.append('shares', shares);
    
    fetch('/game/buy_stock', {
        method: 'POST',
        body: form
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    })
    .catch(error => {
        console.error('Error buying stock:', error);
    });
}

// Real-time notifications
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Confirm actions
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Initialize charts (if Chart.js is loaded)
function initializeCharts() {
    // Market price chart
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
                        scales: {
                            y: {
                                beginAtZero: false
                            }
                        }
                    }
                });
            });
    }
}

// Export functions for global use
window.gameUtils = {
    formatCurrency,
    formatNumber,
    showNotification,
    confirmAction,
    updateGameData,
    refreshMarketData
};