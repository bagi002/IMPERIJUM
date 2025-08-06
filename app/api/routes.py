from flask import jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.api import bp
from app.models import Company, Product, Market, Worker, GameState, User, StockHolding

@bp.route('/companies')
@login_required
def api_companies():
    """API endpoint for company data"""
    companies = []
    for company in current_user.companies:
        companies.append({
            'id': company.id,
            'name': company.name,
            'sector': company.sector,
            'cash': company.cash,
            'stock_price': company.stock_price,
            'employees': company.employees.count(),
            'monthly_profit': company.get_monthly_profit()
        })
    return jsonify(companies)

@bp.route('/market_data')
@login_required
def api_market_data():
    """API endpoint for market data"""
    products = []
    for product in Product.query.all():
        products.append({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'market_price': product.market_price,
            'stock_quantity': product.stock_quantity,
            'company_name': product.company.name,
            'demand_level': product.get_demand_level(),
            'supply_demand_ratio': product.calculate_supply_demand_ratio()
        })
    return jsonify(products)

@bp.route('/leaderboard')
def api_leaderboard():
    """API endpoint for player leaderboard"""
    players = User.query.filter_by(is_ai=False).all()
    
    leaderboard = []
    for player in players:
        leaderboard.append({
            'username': player.username,
            'cash': player.cash,
            'net_worth': player.get_net_worth(),
            'company_count': player.companies.count(),
            'total_revenue': sum([company.monthly_revenue for company in player.companies])
        })
    
    # Sort by net worth descending
    leaderboard.sort(key=lambda x: x['net_worth'], reverse=True)
    return jsonify(leaderboard)

@bp.route('/recent_transactions')
@login_required
def api_recent_transactions():
    """API endpoint for recent market transactions"""
    transactions = Market.query.order_by(Market.transaction_date.desc()).limit(20).all()
    
    transaction_data = []
    for transaction in transactions:
        transaction_data.append({
            'id': transaction.id,
            'product_name': transaction.product.name,
            'quantity': transaction.quantity,
            'price_per_unit': transaction.price_per_unit,
            'total_amount': transaction.total_amount,
            'buyer': transaction.buyer_company.name if transaction.buyer_company else 'Player',
            'seller': transaction.seller_company.name,
            'date': transaction.transaction_date.isoformat()
        })
    
    return jsonify(transaction_data)

@bp.route('/game_state')
@login_required
def api_game_state():
    """API endpoint for enhanced game state with timer"""
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState()
        db.session.add(game_state)
        db.session.commit()
    
    return jsonify({
        'current_turn': game_state.current_turn,
        'players_ready': game_state.players_ready,
        'total_players': User.query.filter_by(is_ai=False).count(),
        'is_processing_turn': game_state.is_processing_turn,
        'game_paused': game_state.game_paused,
        'turn_duration': game_state.turn_duration,
        'time_remaining': game_state.get_time_remaining(),
        'turn_expired': game_state.is_turn_expired(),
        'auto_advance_turn': game_state.auto_advance_turn
    })

@bp.route('/player_stats')
@login_required
def api_player_stats():
    """API endpoint for current player statistics"""
    return jsonify({
        'username': current_user.username,
        'cash': current_user.cash,
        'net_worth': current_user.get_net_worth(),
        'companies_count': current_user.companies.count(),
        'stock_holdings_count': current_user.stock_holdings.count()
    })

@bp.route('/market_summary')
@login_required
def api_market_summary():
    """API endpoint for market analytics"""
    from app.market_engine import MarketEngine
    return jsonify(MarketEngine.get_market_summary())

@bp.route('/company_analytics/<int:company_id>')
@login_required
def api_company_analytics(company_id):
    """API endpoint for detailed company analytics"""
    company = Company.query.get_or_404(company_id)
    if company.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'id': company.id,
        'name': company.name,
        'sector': company.sector,
        'cash': company.cash,
        'stock_price': company.stock_price,
        'valuation': company.calculate_valuation(),
        'monthly_revenue': company.monthly_revenue,
        'monthly_expenses': company.monthly_expenses,
        'monthly_profit': company.get_monthly_profit(),
        'reputation': company.reputation,
        'employee_count': company.employees.count(),
        'product_count': company.products.count(),
        'market_share': {
            'stock_value': company.get_company_value(),
            'total_market': sum([c.get_company_value() for c in Company.query.all()])
        }
    })

@bp.route('/production_status/<int:company_id>')
@login_required
def api_production_status(company_id):
    """API endpoint for company production status"""
    company = Company.query.get_or_404(company_id)
    if company.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    from app.production_engine import ProductionEngine
    production_report = ProductionEngine.get_production_report(company)
    
    return jsonify(production_report)

@bp.route('/production_overview')
@login_required
def api_production_overview():
    """API endpoint for all user companies production overview"""
    companies_production = []
    
    for company in current_user.companies:
        from app.production_engine import ProductionEngine
        report = ProductionEngine.get_production_report(company)
        report['company_id'] = company.id
        report['company_name'] = company.name
        report['sector'] = company.sector
        companies_production.append(report)
    
    return jsonify({
        'companies': companies_production,
        'total_companies': len(companies_production),
        'active_companies': len([c for c in companies_production if c['status'] == 'active'])
    })

@bp.route('/market_events')
@login_required  
def api_recent_market_events():
    """API endpoint for recent market events (simulated)"""
    # In a real implementation, this would query a market_events table
    # For now, return sample recent events
    return jsonify({
        'recent_events': [
            {
                'title': 'Market Update',
                'description': 'Regular market price adjustments based on supply and demand',
                'type': 'market_update',
                'impact': 'neutral',
                'timestamp': datetime.utcnow().isoformat()
            }
        ],
        'events_today': 1,
        'market_volatility': 'normal'
    })