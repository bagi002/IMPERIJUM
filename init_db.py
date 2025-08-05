#!/usr/bin/env python3
"""
Database initialization script for IMPERIJUM game
Creates sample data including AI players, workers, and initial products
"""

import random
from app import create_app, db
from app.models import User, Company, Product, Worker, GameState

# Sample data
COMPANY_NAMES = [
    "Iron Mountain Mining", "Steel Works Corp", "Timber Valley", "Oil Creek Industries",
    "TechManufacturing Inc", "Precision Tools Ltd", "AutoParts Express", "Electronics Hub",
    "SuperMart Chain", "Fashion Boutique", "Food Palace", "Home & Garden Store"
]

RAW_MATERIALS = [
    ("Iron Ore", 25.0), ("Steel", 45.0), ("Wood", 15.0), ("Oil", 60.0),
    ("Coal", 20.0), ("Copper", 35.0), ("Aluminum", 40.0), ("Gold", 1200.0)
]

MANUFACTURED_GOODS = [
    ("Car Parts", 150.0), ("Electronics", 200.0), ("Furniture", 180.0), ("Tools", 75.0),
    ("Machinery", 500.0), ("Appliances", 300.0), ("Textiles", 25.0), ("Chemicals", 80.0)
]

RETAIL_PRODUCTS = [
    ("Consumer Electronics", 400.0), ("Clothing", 50.0), ("Food Items", 8.0), ("Home Goods", 120.0),
    ("Books", 15.0), ("Sports Equipment", 85.0), ("Toys", 25.0), ("Garden Supplies", 35.0)
]

WORKER_NAMES = [
    "John Smith", "Maria Garcia", "David Johnson", "Lisa Chen", "Robert Brown",
    "Sarah Wilson", "Michael Davis", "Jennifer Martinez", "Christopher Lee", "Amanda Taylor",
    "Daniel Anderson", "Jessica Thompson", "Matthew White", "Ashley Rodriguez", "Joshua Harris",
    "Emily Clark", "Andrew Lewis", "Stephanie Walker", "Ryan Hall", "Michelle Young"
]

SPECIALIZATIONS = [
    "general", "manufacturing", "retail", "mining", "logistics", "management",
    "technical", "sales", "quality_control", "maintenance"
]

def create_ai_players(app):
    """Create AI players with companies"""
    with app.app_context():
        print("Creating AI players...")
        
        ai_names = ["AI_Titan", "AI_Mogul", "AI_Empire", "AI_Corp", "AI_Industries"]
        
        for name in ai_names:
            # Check if AI player already exists
            if User.query.filter_by(username=name).first():
                continue
                
            ai_player = User(
                username=name,
                email=f"{name.lower()}@ai.imperijum.com",
                cash=random.randint(80000, 150000),
                is_ai=True
            )
            ai_player.set_password("ai_password")
            db.session.add(ai_player)
            db.session.flush()  # To get the AI player ID
            
            # Create 1-3 companies for each AI player
            num_companies = random.randint(1, 3)
            sectors = ["raw_materials", "manufacturing", "retail"]
            
            for i in range(num_companies):
                sector = random.choice(sectors)
                company_name = f"{name}_{random.choice(COMPANY_NAMES).split()[0]}"
                
                company = Company(
                    name=company_name,
                    sector=sector,
                    owner_id=ai_player.id,
                    cash=random.randint(10000, 50000),
                    stock_price=random.uniform(8.0, 25.0),
                    reputation=random.uniform(40.0, 80.0),
                    monthly_revenue=random.randint(5000, 20000),
                    monthly_expenses=random.randint(3000, 15000)
                )
                db.session.add(company)
        
        db.session.commit()
        print("AI players created successfully!")

def create_products(app):
    """Create initial products for companies"""
    with app.app_context():
        print("Creating products...")
        
        companies = Company.query.all()
        
        for company in companies:
            # Create 1-2 products per company based on sector
            if company.sector == "raw_materials":
                products_list = RAW_MATERIALS
                category = "raw_material"
            elif company.sector == "manufacturing":
                products_list = MANUFACTURED_GOODS
                category = "manufactured"
            else:  # retail
                products_list = RETAIL_PRODUCTS
                category = "retail"
            
            # Create 1-2 products for each company
            num_products = random.randint(1, 2)
            selected_products = random.sample(products_list, min(num_products, len(products_list)))
            
            for product_name, base_price in selected_products:
                # Add some randomness to prices
                price_variation = random.uniform(0.8, 1.2)
                market_price = base_price * price_variation
                
                product = Product(
                    name=f"{company.name} {product_name}",
                    category=category,
                    company_id=company.id,
                    base_cost=market_price * 0.7,  # 30% profit margin
                    selling_price=market_price,
                    market_price=market_price,
                    stock_quantity=random.randint(50, 500),
                    monthly_production=random.randint(20, 200),
                    monthly_demand=random.randint(15, 180)
                )
                db.session.add(product)
        
        db.session.commit()
        print("Products created successfully!")

def create_workers(app):
    """Create available workers"""
    with app.app_context():
        print("Creating workers...")
        
        for name in WORKER_NAMES:
            # Check if worker already exists
            if Worker.query.filter_by(name=name).first():
                continue
                
            skill_level = random.choice(["basic", "skilled", "expert"])
            specialization = random.choice(SPECIALIZATIONS)
            
            # Calculate desired salary based on skill level
            base_salary = 1000
            if skill_level == "skilled":
                base_salary = 1500
            elif skill_level == "expert":
                base_salary = 2500
            
            # Add some randomness
            desired_salary = base_salary + random.randint(-200, 500)
            
            worker = Worker(
                name=name,
                skill_level=skill_level,
                specialization=specialization,
                desired_salary=desired_salary,
                is_employed=False
            )
            db.session.add(worker)
        
        db.session.commit()
        print("Workers created successfully!")

def initialize_game_state(app):
    """Initialize or update game state"""
    with app.app_context():
        print("Initializing game state...")
        
        game_state = GameState.query.first()
        if not game_state:
            game_state = GameState()
            db.session.add(game_state)
        
        # Update total players count
        total_players = User.query.filter_by(is_ai=False).count()
        game_state.total_players = total_players
        
        db.session.commit()
        print("Game state initialized!")

def main():
    """Main initialization function"""
    app = create_app()
    
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created!")
        
        # Initialize data
        create_ai_players(app)
        create_products(app)
        create_workers(app)
        initialize_game_state(app)
        
        print("\n🎮 Database initialization complete!")
        print("🤖 AI players created with companies and products")
        print("👥 Worker pool is ready for hiring")
        print("🏭 Companies are ready for business")
        print("\nYou can now start the game by running: python run.py")

if __name__ == "__main__":
    main()