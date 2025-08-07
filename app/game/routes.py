from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.game import bp
from app.models import User, Company, Product, Market, Worker, Employee, GameState, StockHolding, Loan

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

@bp.route('/buy_product', methods=['POST'])
@login_required
def buy_product():
    """Buy a product from the market"""
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    
    product = Product.query.get_or_404(product_id)
    total_cost = product.market_price * quantity
    
    if current_user.cash < total_cost:
        flash('Insufficient funds', 'error')
        return redirect(url_for('game.market'))
    
    if quantity > product.stock_quantity:
        flash('Not enough stock available', 'error')
        return redirect(url_for('game.market'))
    
    # Create market transaction
    transaction = Market(
        product_id=product_id,
        buyer_company_id=None,  # Direct player purchase
        seller_company_id=product.company_id,
        quantity=quantity,
        price_per_unit=product.market_price,
        total_amount=total_cost
    )
    
    # Update player cash and product stock
    current_user.cash -= total_cost
    product.stock_quantity -= quantity
    
    # Update seller company cash
    product.company.cash += total_cost
    
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'Successfully purchased {quantity} units of {product.name} for ${total_cost:.2f}', 'success')
    return redirect(url_for('game.market'))

@bp.route('/next_turn', methods=['POST'])
@login_required
def next_turn():
    """Player indicates ready for next turn"""
    from app.market_engine import MarketEngine
    
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState()
        db.session.add(game_state)
    
    # This is simplified - in real implementation, track individual player readiness
    game_state.players_ready += 1
    total_players = User.query.filter_by(is_ai=False).count()
    
    if game_state.players_ready >= total_players:
        # All players ready, advance turn and process market
        game_state.current_turn += 1
        game_state.players_ready = 0
        game_state.start_new_turn()  # Use the new method to properly start turn
        
        # Process economic turn using market engine
        turn_results = MarketEngine.process_turn()
        
        # Create enhanced summary for players
        price_changes = len(turn_results['price_changes'])
        significant_changes = len([p for p in turn_results['price_changes'] 
                                 if abs(p['change_percent']) > 5])
        production_count = len(turn_results.get('production_results', []))
        ai_decisions_count = sum(len(decisions) for decisions in turn_results.get('ai_decisions', {}).values())
        
        summary_parts = [f'{price_changes} products updated']
        if significant_changes > 0:
            summary_parts.append(f'{significant_changes} significant price changes')
        if production_count > 0:
            summary_parts.append(f'{production_count} companies produced goods')
        if ai_decisions_count > 0:
            summary_parts.append(f'AI made {ai_decisions_count} decisions')
        if turn_results.get('market_event'):
            summary_parts.append(f'Market event: {turn_results["market_event"].title}')
        
        flash(f'Turn {game_state.current_turn} completed! ' + ', '.join(summary_parts) + '.', 'success')
    else:
        flash(f'Waiting for {total_players - game_state.players_ready} more players', 'info')
    
    db.session.commit()
    return redirect(url_for('game.dashboard'))

@bp.route('/banking')
@login_required
def banking():
    """View banking and loan information"""
    user_loans = current_user.loans.all()
    return render_template('game/banking.html', loans=user_loans)

@bp.route('/apply_loan', methods=['POST'])
@login_required
def apply_loan():
    """Apply for a personal or business loan"""
    loan_type = request.form['loan_type']
    amount = float(request.form['amount'])
    duration = int(request.form['duration'])
    
    # Validate loan amount
    if amount < 1000 or amount > 1000000:
        flash('Loan amount must be between $1,000 and $1,000,000', 'error')
        return redirect(url_for('game.banking'))
    
    # Calculate interest rate based on loan type and duration
    if loan_type == 'business':
        company_id = int(request.form['company_id'])
        company = Company.query.get_or_404(company_id)
        if company.owner_id != current_user.id:
            flash('Access denied', 'error')
            return redirect(url_for('game.banking'))
        
        base_rate = 0.03  # 3% base rate for business loans
        # Better companies get better rates
        reputation_bonus = (100 - company.reputation) * 0.001
        interest_rate = base_rate + reputation_bonus
    else:
        company_id = None
        base_rate = 0.05  # 5% base rate for personal loans
        # Player's net worth affects rate
        net_worth = current_user.get_net_worth()
        if net_worth > 500000:
            wealth_bonus = -0.01  # Rich players get better rates
        elif net_worth < 50000:
            wealth_bonus = 0.02   # Poor players pay more
        else:
            wealth_bonus = 0
        interest_rate = base_rate + wealth_bonus
    
    # Duration penalty
    duration_penalty = (duration - 12) * 0.001
    interest_rate += duration_penalty
    
    # Ensure reasonable bounds
    interest_rate = max(0.02, min(0.15, interest_rate))
    
    # Calculate monthly payment
    monthly_rate = interest_rate / 12
    monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** duration) / \
                     ((1 + monthly_rate) ** duration - 1)
    
    # Create loan
    loan = Loan(
        user_id=current_user.id,
        company_id=company_id,
        amount=amount,
        interest_rate=interest_rate,
        monthly_payment=monthly_payment,
        remaining_amount=amount,
        months_remaining=duration
    )
    
    # Add money to appropriate account
    if loan_type == 'business':
        company.cash += amount
        flash(f'Business loan approved! ${amount:,.0f} added to {company.name}', 'success')
    else:
        current_user.cash += amount
        flash(f'Personal loan approved! ${amount:,.0f} added to your account', 'success')
    
    db.session.add(loan)
    db.session.commit()
    
    return redirect(url_for('game.banking'))