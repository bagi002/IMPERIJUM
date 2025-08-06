from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from app import db

class User(UserMixin, db.Model):
    """Player/User model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    cash = db.Column(db.Float, default=100000.0)  # Player's cash
    is_ai = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    companies = db.relationship('Company', backref='owner', lazy='dynamic')
    stock_holdings = db.relationship('StockHolding', backref='holder', lazy='dynamic')
    loans = db.relationship('Loan', backref='borrower', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Generate a password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify if reset token is valid and not expired"""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        if self.reset_token != token:
            return False
        if datetime.utcnow() > self.reset_token_expiry:
            return False
        return True
    
    def clear_reset_token(self):
        """Clear the reset token after successful password reset"""
        self.reset_token = None
        self.reset_token_expiry = None
    
    def get_net_worth(self):
        """Calculate total net worth including cash and stock values"""
        stock_value = sum([holding.shares * holding.company.stock_price 
                          for holding in self.stock_holdings])
        company_values = sum([company.get_company_value() 
                             for company in self.companies])
        return self.cash + stock_value + company_values

class Company(db.Model):
    """Company model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(50), nullable=False)  # 'raw_materials', 'manufacturing', 'retail'
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cash = db.Column(db.Float, default=0.0)
    stock_price = db.Column(db.Float, default=10.0)
    total_shares = db.Column(db.Integer, default=1000)
    available_shares = db.Column(db.Integer, default=0)  # Shares for sale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Company stats
    reputation = db.Column(db.Float, default=50.0)  # 0-100
    monthly_revenue = db.Column(db.Float, default=0.0)
    monthly_expenses = db.Column(db.Float, default=0.0)
    
    # Relationships
    employees = db.relationship('Employee', backref='company', lazy='dynamic')
    products = db.relationship('Product', backref='company', lazy='dynamic')
    stock_holdings = db.relationship('StockHolding', backref='company', lazy='dynamic')
    loans = db.relationship('Loan', backref='company', lazy='dynamic')
    
    def get_company_value(self):
        """Calculate company market value"""
        return self.stock_price * self.total_shares
    
    def get_monthly_profit(self):
        return self.monthly_revenue - self.monthly_expenses
    
    def calculate_valuation(self):
        """Calculate comprehensive company valuation based on multiple factors"""
        # Base valuation on cash and assets
        base_value = self.cash
        
        # Add value from products and inventory
        product_value = sum([p.stock_quantity * p.market_price for p in self.products])
        base_value += product_value
        
        # Revenue multiplier based on sector
        sector_multipliers = {
            'raw_materials': 3.0,
            'manufacturing': 4.0,
            'retail': 2.5
        }
        
        multiplier = sector_multipliers.get(self.sector, 3.0)
        revenue_value = self.monthly_revenue * multiplier
        
        # Reputation factor (0.5 to 1.5 multiplier)
        reputation_factor = 0.5 + (self.reputation / 100.0)
        
        # Employee value (skilled workforce adds value)
        employee_value = sum([e.salary * 0.5 for e in self.employees]) * 12  # Annual salary value
        
        total_value = (base_value + revenue_value + employee_value) * reputation_factor
        return max(total_value, 1000)  # Minimum value of $1000
    
    def update_stock_price(self):
        """Update stock price based on company valuation"""
        new_valuation = self.calculate_valuation()
        new_price = new_valuation / self.total_shares
        
        # Gradual price adjustment to avoid sudden spikes
        price_change = (new_price - self.stock_price) * 0.3
        self.stock_price = max(self.stock_price + price_change, 1.0)  # Minimum $1 per share
        
        return self.stock_price

class Worker(db.Model):
    """Worker/Employee pool model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    skill_level = db.Column(db.String(20), nullable=False)  # 'basic', 'skilled', 'expert'
    specialization = db.Column(db.String(50), nullable=False)  # 'general', 'manufacturing', 'retail', etc.
    desired_salary = db.Column(db.Float, nullable=False)
    is_employed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Employee(db.Model):
    """Employee assignment model"""
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    hired_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    worker = db.relationship('Worker', backref='employment')

class Product(db.Model):
    """Product model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'raw_material', 'manufactured', 'retail'
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    base_cost = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    market_price = db.Column(db.Float, nullable=False)  # Current market price
    stock_quantity = db.Column(db.Integer, default=0)
    monthly_production = db.Column(db.Integer, default=0)
    monthly_demand = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_supply_demand_ratio(self):
        """Calculate supply/demand ratio for pricing"""
        total_supply = Product.query.filter_by(name=self.name).with_entities(
            db.func.sum(Product.stock_quantity)
        ).scalar() or 0
        
        total_demand = Product.query.filter_by(name=self.name).with_entities(
            db.func.sum(Product.monthly_demand)
        ).scalar() or 1
        
        return total_supply / max(total_demand, 1)
    
    def update_market_price(self, volatility=0.1):
        """Update market price based on supply and demand"""
        from config import Config
        volatility = getattr(Config, 'MARKET_VOLATILITY', 0.1)
        
        supply_demand_ratio = self.calculate_supply_demand_ratio()
        
        # Price adjustment based on supply/demand
        # High supply (>1.5) = lower prices
        # Low supply (<0.5) = higher prices
        if supply_demand_ratio > 1.5:
            price_factor = 0.8 + (0.2 * min(supply_demand_ratio / 3.0, 1.0))
        elif supply_demand_ratio < 0.5:
            price_factor = 1.2 + (0.8 * (1.0 - supply_demand_ratio * 2))
        else:
            price_factor = 1.0
        
        # Add random market volatility
        import random
        volatility_factor = 1 + random.uniform(-volatility, volatility)
        
        new_price = self.base_cost * price_factor * volatility_factor
        
        # Gradual price adjustment
        price_change = (new_price - self.market_price) * 0.4
        self.market_price = max(self.market_price + price_change, self.base_cost * 0.5)
        
        return self.market_price
    
    def get_demand_level(self):
        """Get textual representation of demand level"""
        ratio = self.calculate_supply_demand_ratio()
        if ratio > 2.0:
            return "Very Low"
        elif ratio > 1.5:
            return "Low"
        elif ratio > 0.8:
            return "Moderate"
        elif ratio > 0.5:
            return "High"
        else:
            return "Very High"

class Market(db.Model):
    """Market transactions and pricing"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    buyer_company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    seller_company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='market_transactions')
    buyer_company = db.relationship('Company', foreign_keys=[buyer_company_id], backref='purchases')
    seller_company = db.relationship('Company', foreign_keys=[seller_company_id], backref='sales')

class StockHolding(db.Model):
    """Stock ownership model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)

class Loan(db.Model):
    """Loan model for players and companies"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    monthly_payment = db.Column(db.Float, nullable=False)
    remaining_amount = db.Column(db.Float, nullable=False)
    months_remaining = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GameState(db.Model):
    """Global game state"""
    id = db.Column(db.Integer, primary_key=True)
    current_turn = db.Column(db.Integer, default=1)
    turn_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    turn_duration = db.Column(db.Integer, default=300)  # Turn time in seconds (5 minutes default)
    players_ready = db.Column(db.Integer, default=0)
    total_players = db.Column(db.Integer, default=0)
    is_processing_turn = db.Column(db.Boolean, default=False)
    auto_advance_turn = db.Column(db.Boolean, default=True)  # Auto-advance when timer expires
    game_paused = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_time_remaining(self):
        """Get remaining time for current turn in seconds"""
        if self.game_paused or self.is_processing_turn:
            return self.turn_duration
        
        elapsed = (datetime.utcnow() - self.turn_start_time).total_seconds()
        remaining = max(0, self.turn_duration - elapsed)
        return int(remaining)
    
    def is_turn_expired(self):
        """Check if current turn has expired"""
        if self.game_paused or self.is_processing_turn:
            return False
        return self.get_time_remaining() <= 0
    
    def start_new_turn(self):
        """Start a new turn"""
        self.current_turn += 1
        self.turn_start_time = datetime.utcnow()
        self.players_ready = 0
        self.is_processing_turn = False