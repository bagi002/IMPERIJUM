from flask import jsonify, request
from flask_login import login_required, current_user
from app import db
from app.api import bp
from app.models import Company, Product, Market, Worker, GameState

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
            'company_name': product.company.name
        })
    return jsonify(products)

@bp.route('/game_state')
@login_required
def api_game_state():
    """API endpoint for game state"""
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState()
        db.session.add(game_state)
        db.session.commit()
    
    return jsonify({
        'current_turn': game_state.current_turn,
        'players_ready': game_state.players_ready,
        'total_players': game_state.total_players,
        'game_paused': game_state.game_paused
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