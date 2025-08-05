from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
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
    
    # Relationships
    companies = db.relationship('Company', backref='owner', lazy='dynamic')
    stock_holdings = db.relationship('StockHolding', backref='holder', lazy='dynamic')
    loans = db.relationship('Loan', backref='borrower', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
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
    players_ready = db.Column(db.Integer, default=0)
    total_players = db.Column(db.Integer, default=0)
    game_paused = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)