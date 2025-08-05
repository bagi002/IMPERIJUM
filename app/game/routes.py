from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.game import bp
from app.models import User, Company, Product, Market, Worker, Employee, GameState, StockHolding

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main game dashboard"""
    user_companies = current_user.companies.all()
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState()
        db.session.add(game_state)
        db.session.commit()
    
    return render_template('game/dashboard.html', 
                         companies=user_companies, 
                         game_state=game_state)

@bp.route('/companies')
@login_required
def companies():
    """View and manage companies"""
    user_companies = current_user.companies.all()
    return render_template('game/companies.html', companies=user_companies)

@bp.route('/create_company', methods=['GET', 'POST'])
@login_required
def create_company():
    """Create a new company"""
    if request.method == 'POST':
        name = request.form['name']
        sector = request.form['sector']
        initial_investment = float(request.form['initial_investment'])
        
        if current_user.cash < initial_investment:
            flash('Insufficient funds')
            return redirect(url_for('game.create_company'))
        
        # Check if name is unique
        if Company.query.filter_by(name=name).first():
            flash('Company name already exists')
            return redirect(url_for('game.create_company'))
        
        company = Company(
            name=name,
            sector=sector,
            owner_id=current_user.id,
            cash=initial_investment
        )
        
        current_user.cash -= initial_investment
        db.session.add(company)
        db.session.commit()
        
        flash(f'Company "{name}" created successfully!')
        return redirect(url_for('game.companies'))
    
    return render_template('game/create_company.html')

@bp.route('/company/<int:company_id>')
@login_required
def company_detail(company_id):
    """View detailed company information"""
    company = Company.query.get_or_404(company_id)
    if company.owner_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('game.companies'))
    
    employees = company.employees.all()
    products = company.products.all()
    return render_template('game/company_detail.html', 
                         company=company, 
                         employees=employees, 
                         products=products)

@bp.route('/market')
@login_required
def market():
    """View market and available products"""
    products = Product.query.all()
    recent_transactions = Market.query.order_by(Market.transaction_date.desc()).limit(20).all()
    return render_template('game/market.html', 
                         products=products, 
                         transactions=recent_transactions)

@bp.route('/workers')
@login_required
def workers():
    """View available workers"""
    available_workers = Worker.query.filter_by(is_employed=False).all()
    user_employees = []
    for company in current_user.companies:
        user_employees.extend(company.employees.all())
    
    return render_template('game/workers.html', 
                         available_workers=available_workers,
                         employees=user_employees)

@bp.route('/hire_worker', methods=['POST'])
@login_required
def hire_worker():
    """Hire a worker for a company"""
    worker_id = int(request.form['worker_id'])
    company_id = int(request.form['company_id'])
    salary = float(request.form['salary'])
    
    worker = Worker.query.get_or_404(worker_id)
    company = Company.query.get_or_404(company_id)
    
    if company.owner_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('game.workers'))
    
    if worker.is_employed:
        flash('Worker already employed')
        return redirect(url_for('game.workers'))
    
    if salary < worker.desired_salary:
        flash(f'Salary too low. Worker expects at least ${worker.desired_salary}')
        return redirect(url_for('game.workers'))
    
    employee = Employee(
        worker_id=worker_id,
        company_id=company_id,
        salary=salary
    )
    
    worker.is_employed = True
    db.session.add(employee)
    db.session.commit()
    
    flash(f'Worker {worker.name} hired successfully!')
    return redirect(url_for('game.workers'))

@bp.route('/stock_exchange')
@login_required
def stock_exchange():
    """View stock exchange"""
    companies = Company.query.filter(Company.available_shares > 0).all()
    user_holdings = current_user.stock_holdings.all()
    return render_template('game/stock_exchange.html', 
                         companies=companies,
                         holdings=user_holdings)

@bp.route('/buy_stock', methods=['POST'])
@login_required
def buy_stock():
    """Buy company stock"""
    company_id = int(request.form['company_id'])
    shares = int(request.form['shares'])
    
    company = Company.query.get_or_404(company_id)
    total_cost = shares * company.stock_price
    
    if current_user.cash < total_cost:
        flash('Insufficient funds')
        return redirect(url_for('game.stock_exchange'))
    
    if shares > company.available_shares:
        flash('Not enough shares available')
        return redirect(url_for('game.stock_exchange'))
    
    # Create or update stock holding
    holding = StockHolding.query.filter_by(
        user_id=current_user.id,
        company_id=company_id
    ).first()
    
    if holding:
        # Update existing holding
        avg_price = (holding.shares * holding.purchase_price + shares * company.stock_price) / (holding.shares + shares)
        holding.shares += shares
        holding.purchase_price = avg_price
    else:
        # Create new holding
        holding = StockHolding(
            user_id=current_user.id,
            company_id=company_id,
            shares=shares,
            purchase_price=company.stock_price
        )
        db.session.add(holding)
    
    current_user.cash -= total_cost
    company.available_shares -= shares
    company.cash += total_cost
    
    db.session.commit()
    flash(f'Purchased {shares} shares of {company.name}')
    return redirect(url_for('game.stock_exchange'))

@bp.route('/next_turn', methods=['POST'])
@login_required
def next_turn():
    """Player indicates ready for next turn"""
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState()
        db.session.add(game_state)
    
    # This is simplified - in real implementation, track individual player readiness
    game_state.players_ready += 1
    total_players = User.query.filter_by(is_ai=False).count()
    
    if game_state.players_ready >= total_players:
        # All players ready, advance turn
        game_state.current_turn += 1
        game_state.players_ready = 0
        # Process turn logic here (AI moves, market updates, etc.)
        flash(f'Turn {game_state.current_turn} started!')
    else:
        flash(f'Waiting for {total_players - game_state.players_ready} more players')
    
    db.session.commit()
    return redirect(url_for('game.dashboard'))