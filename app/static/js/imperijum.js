/* IMPERIJUM Game JavaScript - Real-time Updates and UI Enhancements */

class ImperijumGame {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.dashboardUpdateTimer = null;
        this.init();
    }

    init() {
        this.startDashboardUpdates();
        this.initEventHandlers();
        this.updatePlayerStats();
    }

    startDashboardUpdates() {
        // Only start updates on game pages
        if (window.location.pathname.includes('/dashboard') || 
            window.location.pathname.includes('/market') ||
            window.location.pathname.includes('/companies')) {
            
            this.dashboardUpdateTimer = setInterval(() => {
                this.updateDashboardData();
            }, this.updateInterval);
        }
    }

    stopDashboardUpdates() {
        if (this.dashboardUpdateTimer) {
            clearInterval(this.dashboardUpdateTimer);
            this.dashboardUpdateTimer = null;
        }
    }

    async updateDashboardData() {
        try {
            // Update player stats
            await this.updatePlayerStats();
            
            // Update market data if on market page
            if (window.location.pathname.includes('/market')) {
                await this.updateMarketData();
            }
            
            // Update game state
            await this.updateGameState();
            
            console.log('Dashboard data updated');
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }

    async updatePlayerStats() {
        try {
            const response = await fetch('/api/player_stats');
            const stats = await response.json();
            
            // Update cash display in navbar
            const cashElement = document.querySelector('.navbar .nav-link:contains("$")');
            if (cashElement) {
                const usernameText = cashElement.textContent.split('(')[0].trim();
                cashElement.innerHTML = `👤 ${usernameText} ($${this.formatCurrency(stats.cash)})`;
            }
            
            // Update dashboard stats if elements exist
            this.updateElementText('#player-cash', this.formatCurrency(stats.cash));
            this.updateElementText('#player-net-worth', this.formatCurrency(stats.net_worth));
            this.updateElementText('#company-count', stats.company_count);
            this.updateElementText('#employee-count', stats.employee_count);
            
        } catch (error) {
            console.error('Error updating player stats:', error);
        }
    }

    async updateMarketData() {
        try {
            const response = await fetch('/api/market_data');
            const products = await response.json();
            
            // Update product prices in market table
            products.forEach(product => {
                const priceElement = document.querySelector(`#product-${product.id}-price`);
                const stockElement = document.querySelector(`#product-${product.id}-stock`);
                const demandElement = document.querySelector(`#product-${product.id}-demand`);
                
                if (priceElement) {
                    priceElement.textContent = '$' + product.market_price.toFixed(2);
                }
                if (stockElement) {
                    stockElement.textContent = product.stock_quantity.toLocaleString();
                }
                if (demandElement) {
                    demandElement.textContent = product.demand_level;
                    // Update color based on demand
                    demandElement.className = this.getDemandClass(product.demand_level);
                }
            });
            
        } catch (error) {
            console.error('Error updating market data:', error);
        }
    }

    async updateGameState() {
        try {
            const response = await fetch('/api/game_state');
            const gameState = await response.json();
            
            // Update turn information
            this.updateElementText('#current-turn', gameState.current_turn);
            this.updateElementText('#players-ready', gameState.players_ready);
            this.updateElementText('#total-players', gameState.total_players);
            
            // Update turn progress bar if exists
            const progressBar = document.querySelector('#turn-progress');
            if (progressBar && gameState.total_players > 0) {
                const progress = (gameState.players_ready / gameState.total_players) * 100;
                progressBar.style.width = progress + '%';
                progressBar.setAttribute('aria-valuenow', progress);
            }
            
        } catch (error) {
            console.error('Error updating game state:', error);
        }
    }

    initEventHandlers() {
        // Auto-refresh market data button
        const refreshButton = document.querySelector('#refresh-market');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.updateMarketData();
                this.showNotification('Market data refreshed', 'success');
            });
        }

        // Confirm dangerous actions
        document.querySelectorAll('.btn-danger').forEach(button => {
            button.addEventListener('click', (e) => {
                if (!confirm('Are you sure you want to perform this action?')) {
                    e.preventDefault();
                }
            });
        });

        // Auto-calculate loan payments
        const loanForm = document.querySelector('#loan-form');
        if (loanForm) {
            const amountInput = loanForm.querySelector('input[name="amount"]');
            const durationSelect = loanForm.querySelector('select[name="duration"]');
            
            if (amountInput && durationSelect) {
                [amountInput, durationSelect].forEach(element => {
                    element.addEventListener('change', () => {
                        this.calculateLoanPayment();
                    });
                });
            }
        }

        // Real-time stock cost calculation
        document.querySelectorAll('[id^="shares"]').forEach(input => {
            input.addEventListener('input', (e) => {
                const companyId = e.target.id.replace('shares', '');
                this.updateStockCost(companyId);
            });
        });
    }

    calculateLoanPayment() {
        const form = document.querySelector('#loan-form');
        if (!form) return;

        const amount = parseFloat(form.querySelector('input[name="amount"]').value) || 0;
        const duration = parseInt(form.querySelector('select[name="duration"]').value) || 0;
        const loanType = form.querySelector('select[name="loan_type"]').value;

        if (amount > 0 && duration > 0) {
            // Calculate interest rate
            let baseRate = loanType === 'business' ? 0.03 : 0.05;
            let durationPenalty = (duration - 12) * 0.001;
            let interestRate = baseRate + durationPenalty;

            // Calculate monthly payment
            let monthlyRate = interestRate / 12;
            let monthlyPayment = amount * (monthlyRate * Math.pow(1 + monthlyRate, duration)) / 
                               (Math.pow(1 + monthlyRate, duration) - 1);
            let totalRepayment = monthlyPayment * duration;

            // Update display
            this.updateElementText('#calculated-rate', (interestRate * 100).toFixed(1) + '%');
            this.updateElementText('#calculated-payment', '$' + monthlyPayment.toFixed(0));
            this.updateElementText('#calculated-total', '$' + totalRepayment.toFixed(0));
        }
    }

    updateStockCost(companyId) {
        const sharesInput = document.querySelector(`#shares${companyId}`);
        const priceElement = document.querySelector(`#stock-price-${companyId}`);
        
        if (sharesInput && priceElement) {
            const shares = parseInt(sharesInput.value) || 0;
            const price = parseFloat(priceElement.textContent.replace('$', '')) || 0;
            const subtotal = shares * price;
            const fee = subtotal * 0.01;
            const total = subtotal + fee;

            this.updateElementText(`#total-cost-${companyId}`, '$' + subtotal.toFixed(2));
            this.updateElementText(`#trading-fee-${companyId}`, '$' + fee.toFixed(2));
            this.updateElementText(`#total-amount-${companyId}`, '$' + total.toFixed(2));
        }
    }

    updateElementText(selector, text) {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = text;
        }
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount).replace('$', '');
    }

    getDemandClass(demandLevel) {
        const classes = {
            'Very High': 'badge bg-danger',
            'High': 'badge bg-warning',
            'Moderate': 'badge bg-info',
            'Low': 'badge bg-secondary',
            'Very Low': 'badge bg-dark'
        };
        return classes[demandLevel] || 'badge bg-secondary';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    // Utility method to refresh page data
    async refreshPageData() {
        await this.updateDashboardData();
        this.showNotification('Page data refreshed', 'success');
    }
}

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.imperijumGame = new ImperijumGame();
});

// Clean up when leaving page
window.addEventListener('beforeunload', () => {
    if (window.imperijumGame) {
        window.imperijumGame.stopDashboardUpdates();
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+R or F5 - Refresh page data
    if ((e.ctrlKey && e.key === 'r') || e.key === 'F5') {
        e.preventDefault();
        if (window.imperijumGame) {
            window.imperijumGame.refreshPageData();
        }
    }
});

// Utility functions for templates
window.ImperijumUtils = {
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    },
    
    formatNumber: (number) => {
        return new Intl.NumberFormat('en-US').format(number);
    },
    
    calculatePercentChange: (oldValue, newValue) => {
        if (oldValue === 0) return newValue > 0 ? 100 : 0;
        return ((newValue - oldValue) / oldValue) * 100;
    },
    
    getTimeAgo: (date) => {
        const now = new Date();
        const past = new Date(date);
        const diffMs = now - past;
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minutes ago`;
        if (diffHours < 24) return `${diffHours} hours ago`;
        return `${diffDays} days ago`;
    }
};