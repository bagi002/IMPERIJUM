/**
 * Real-time WebSocket functionality for IMPERIJUM
 * Handles Socket.IO connections and real-time game updates
 */

class RealTimeManager {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.init();
    }

    init() {
        // Initialize Socket.IO connection
        this.socket = io();
        this.setupEventHandlers();
        this.setupConnectionHandlers();
    }

    setupConnectionHandlers() {
        this.socket.on('connect', () => {
            console.log('Connected to IMPERIJUM real-time server');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
            
            // Join game updates
            this.socket.emit('join_game');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from IMPERIJUM server');
            this.isConnected = false;
            this.updateConnectionStatus(false);
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.handleReconnection();
        });
    }

    setupEventHandlers() {
        // Game state updates
        this.socket.on('game_state_update', (data) => {
            this.updateGameState(data);
        });

        // Market updates
        this.socket.on('market_update', (data) => {
            this.handleMarketUpdate(data);
        });

        // Turn completion
        this.socket.on('turn_complete', (data) => {
            this.handleTurnComplete(data);
        });

        // Notifications
        this.socket.on('notification', (data) => {
            this.showNotification(data);
        });

        // Company events
        this.socket.on('company_event', (data) => {
            this.handleCompanyEvent(data);
        });

        // Market events
        this.socket.on('market_event', (data) => {
            this.handleMarketEvent(data);
        });
    }

    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connection-status');
        if (statusIndicator) {
            statusIndicator.className = connected ? 
                'badge bg-success' : 'badge bg-danger';
            statusIndicator.textContent = connected ? 
                'Online' : 'Offline';
        }
    }

    updateGameState(data) {
        // Update turn counter
        const turnCounter = document.getElementById('current-turn');
        if (turnCounter) {
            turnCounter.textContent = `Turn ${data.current_turn}`;
        }

        // Update processing status
        const processingStatus = document.getElementById('processing-status');
        if (processingStatus) {
            processingStatus.style.display = data.is_processing ? 'block' : 'none';
        }

        // Update player counts
        const playerCount = document.getElementById('player-count');
        if (playerCount) {
            playerCount.textContent = `${data.ready_players}/${data.total_players} ready`;
        }
    }

    handleMarketUpdate(data) {
        console.log('Market update received:', data);
        
        // Update market prices if on market page
        if (window.location.pathname.includes('/market')) {
            this.updateMarketPrices(data.price_changes);
        }

        // Show notification for significant price changes
        const significantChanges = data.price_changes.filter(change => 
            Math.abs(change.change_percent) > 5
        );

        if (significantChanges.length > 0) {
            this.showNotification({
                type: 'info',
                message: `Market update: ${significantChanges.length} products had significant price changes`,
                timestamp: data.timestamp
            });
        }
    }

    updateMarketPrices(priceChanges) {
        priceChanges.forEach(change => {
            const priceElement = document.querySelector(`[data-product-id="${change.product}"] .price`);
            if (priceElement) {
                priceElement.textContent = `$${change.new_price.toFixed(2)}`;
                
                // Add visual indicator for price change
                const changeClass = change.change_percent > 0 ? 'text-success' : 'text-danger';
                priceElement.className = `price ${changeClass}`;
                
                // Remove class after animation
                setTimeout(() => {
                    priceElement.className = 'price';
                }, 2000);
            }
        });
    }

    handleTurnComplete(data) {
        console.log('Turn completed:', data);
        
        this.showNotification({
            type: 'success',
            message: `Turn ${data.turn_number} completed! ${data.summary}`,
            timestamp: data.timestamp
        });

        // Refresh relevant data
        if (typeof refreshDashboard === 'function') {
            refreshDashboard();
        }
    }

    handleCompanyEvent(data) {
        console.log('Company event:', data);
        
        this.showNotification({
            type: 'info',
            message: `${data.company_name}: ${data.message}`,
            timestamp: data.timestamp
        });
    }

    handleMarketEvent(data) {
        console.log('Market event:', data);
        
        // Show prominent notification for market events
        this.showMarketEventModal(data);
    }

    showNotification(data) {
        // Create toast notification
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) return;

        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = 'toast show';
        toast.id = toastId;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        const typeIcon = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        };

        toast.innerHTML = `
            <div class="toast-header">
                <span class="me-2">${typeIcon[data.type] || 'ℹ️'}</span>
                <strong class="me-auto">IMPERIJUM</strong>
                <small class="text-muted">${this.formatTime(data.timestamp)}</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${data.message}
            </div>
        `;

        toastContainer.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            const toastElement = document.getElementById(toastId);
            if (toastElement) {
                toastElement.remove();
            }
        }, 5000);
    }

    showMarketEventModal(data) {
        // Create modal for important market events
        const modalHtml = `
            <div class="modal fade" id="marketEventModal" tabindex="-1" aria-labelledby="marketEventModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-warning">
                            <h5 class="modal-title" id="marketEventModalLabel">📰 Market News</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <h6>${data.title}</h6>
                            <p>${data.description}</p>
                            <p><strong>Affected Sectors:</strong> ${data.affected_sectors.join(', ')}</p>
                            <p><strong>Market Impact:</strong> <span class="badge bg-${data.impact === 'positive' ? 'success' : data.impact === 'negative' ? 'danger' : 'secondary'}">${data.impact}</span></p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Got it!</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        const existingModal = document.getElementById('marketEventModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('marketEventModal'));
        modal.show();
    }

    formatTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString();
    }

    handleReconnection() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff
            
            setTimeout(() => {
                console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.socket.connect();
            }, delay);
        }
    }

    // Public methods for other scripts to use
    emitPlayerReady() {
        if (this.isConnected) {
            this.socket.emit('player_ready');
        }
    }
}

// Initialize real-time manager when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.realTimeManager = new RealTimeManager();
});

// Helper function to add connection status indicator to navbar
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        const statusHtml = `
            <li class="nav-item d-flex align-items-center me-2">
                <span id="connection-status" class="badge bg-secondary">Connecting...</span>
            </li>
        `;
        navbar.insertAdjacentHTML('afterbegin', statusHtml);
    }
});