"""
WebSocket event handlers for real-time game updates
"""
from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, disconnect
from app import socketio, db
from app.models import GameState, User, Market
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@socketio.on('connect')
def on_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        logger.info(f"User {current_user.username} connected to WebSocket")
        # Join user-specific room for personalized updates
        join_room(f'user_{current_user.id}')
        # Join general game room for global updates
        join_room('game_updates')
        
        # Send current game state to the newly connected user
        game_state = GameState.query.first()
        if game_state:
            emit('game_state_update', {
                'current_turn': game_state.current_turn,
                'is_processing': game_state.is_processing_turn,
                'total_players': User.query.filter_by(is_ai=False).count(),
                'ready_players': game_state.ready_players
            })
        
        # Send welcome message
        emit('notification', {
            'type': 'success',
            'message': 'Connected to IMPERIJUM real-time updates!',
            'timestamp': str(datetime.utcnow())
        })
    else:
        disconnect()

@socketio.on('disconnect')
def on_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        logger.info(f"User {current_user.username} disconnected from WebSocket")
        leave_room(f'user_{current_user.id}')
        leave_room('game_updates')

@socketio.on('join_game')
def on_join_game():
    """Handle player joining the game"""
    if current_user.is_authenticated:
        join_room('game_updates')
        emit('notification', {
            'type': 'info',
            'message': f'{current_user.username} joined the game!',
            'timestamp': str(datetime.utcnow())
        }, room='game_updates')

@socketio.on('player_ready')
def on_player_ready():
    """Handle player signaling ready for next turn"""
    if current_user.is_authenticated:
        game_state = GameState.query.first()
        if game_state and not game_state.is_processing_turn:
            # Logic for marking player as ready will be implemented in game engine
            emit('notification', {
                'type': 'info',
                'message': f'{current_user.username} is ready for the next turn!',
                'timestamp': str(datetime.utcnow())
            }, room='game_updates')

def broadcast_market_update(price_changes):
    """Broadcast market price changes to all connected players"""
    socketio.emit('market_update', {
        'price_changes': price_changes,
        'timestamp': str(datetime.utcnow())
    }, room='game_updates')

def broadcast_turn_complete(turn_data):
    """Broadcast turn completion to all players"""
    socketio.emit('turn_complete', {
        'turn_number': turn_data['turn_number'],
        'summary': turn_data['summary'],
        'timestamp': str(datetime.utcnow())
    }, room='game_updates')

def send_personal_notification(user_id, notification):
    """Send personal notification to specific user"""
    socketio.emit('notification', {
        'type': notification.get('type', 'info'),
        'message': notification['message'],
        'timestamp': str(datetime.utcnow())
    }, room=f'user_{user_id}')

def broadcast_company_event(event_data):
    """Broadcast company-related events"""
    socketio.emit('company_event', {
        'event_type': event_data['type'],
        'company_name': event_data['company_name'],
        'message': event_data['message'],
        'timestamp': str(datetime.utcnow())
    }, room='game_updates')

def broadcast_market_event(event_data):
    """Broadcast market events and news"""
    socketio.emit('market_event', {
        'event_type': event_data['type'],
        'title': event_data['title'],
        'description': event_data['description'],
        'affected_sectors': event_data.get('affected_sectors', []),
        'impact': event_data.get('impact', 'neutral'),
        'timestamp': str(datetime.utcnow())
    }, room='game_updates')