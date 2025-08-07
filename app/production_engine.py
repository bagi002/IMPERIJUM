"""
Company Production System for IMPERIJUM
Handles automated production for companies based on workers and resources
"""

from app import db
from app.models import Company, Product, Employee, Worker
import random

class ProductionEngine:
    """Manages automated company production"""
    
    @staticmethod
    def process_company_production(company):
        """Process production for a single company"""
        if not company.employees.count():
            return {
                'company_id': company.id,
                'production': 0,
                'reason': 'No employees'
            }
        
        # Calculate base production capacity
        base_production = ProductionEngine.calculate_production_capacity(company)
        
        # Apply efficiency modifiers
        efficiency = ProductionEngine.calculate_efficiency(company)
        
        # Calculate actual production
        actual_production = int(base_production * efficiency)
        
        # Create or update products
        products_created = ProductionEngine.create_products(company, actual_production)
        
        # Deduct production costs
        production_costs = ProductionEngine.calculate_production_costs(company, actual_production)
        
        if company.cash >= production_costs:
            company.cash -= production_costs
            company.monthly_expenses += production_costs
        else:
            # Reduce production if insufficient funds
            affordable_production = int(company.cash / (production_costs / actual_production)) if production_costs > 0 else 0
            actual_production = affordable_production
            products_created = ProductionEngine.create_products(company, actual_production)
            company.cash = 0
            company.monthly_expenses += company.cash
        
        db.session.commit()
        
        return {
            'company_id': company.id,
            'production': actual_production,
            'products_created': products_created,
            'production_costs': production_costs,
            'efficiency': efficiency
        }
    
    @staticmethod
    def calculate_production_capacity(company):
        """Calculate base production capacity based on employees"""
        total_capacity = 0
        
        for employee in company.employees:
            worker = employee.worker
            
            # Base capacity per worker
            base_capacity = 10
            
            # Skill multiplier
            skill_multipliers = {
                'basic': 1.0,
                'skilled': 1.5,
                'expert': 2.0
            }
            skill_multiplier = skill_multipliers.get(worker.skill_level, 1.0)
            
            # Specialization bonus
            specialization_bonus = 1.0
            if company.sector == 'raw_material' and worker.specialization in ['mining', 'general']:
                specialization_bonus = 1.3
            elif company.sector == 'manufacturing' and worker.specialization in ['manufacturing', 'technical', 'general']:
                specialization_bonus = 1.3
            elif company.sector == 'retail' and worker.specialization in ['retail', 'general']:
                specialization_bonus = 1.3
            
            worker_capacity = base_capacity * skill_multiplier * specialization_bonus
            total_capacity += worker_capacity
        
        return total_capacity
    
    @staticmethod
    def calculate_efficiency(company):
        """Calculate production efficiency based on various factors"""
        base_efficiency = 0.8  # 80% base efficiency
        
        # Cash reserves efficiency bonus (well-funded companies are more efficient)
        cash_ratio = company.cash / 10000  # Normalize by 10k
        cash_bonus = min(0.2, cash_ratio * 0.05)  # Max 20% bonus
        
        # Employee satisfaction (simulated based on salary competitiveness)
        satisfaction_bonus = 0.0
        if company.employees.count() > 0:
            avg_salary = sum([e.salary for e in company.employees]) / company.employees.count()
            market_avg_salary = 2000  # Approximate market average
            if avg_salary > market_avg_salary:
                satisfaction_bonus = min(0.15, (avg_salary - market_avg_salary) / market_avg_salary * 0.1)
        
        # Company reputation bonus
        reputation_bonus = (company.reputation - 50) / 100 * 0.1  # Max 10% bonus/penalty
        
        # Random factor for some variability
        random_factor = random.uniform(0.9, 1.1)
        
        efficiency = (base_efficiency + cash_bonus + satisfaction_bonus + reputation_bonus) * random_factor
        return max(0.3, min(1.5, efficiency))  # Clamp between 30% and 150%
    
    @staticmethod
    def create_products(company, production_amount):
        """Create products based on company sector and production amount"""
        if production_amount <= 0:
            return []
        
        products_created = []
        
        # Define products by sector
        sector_products = {
            'raw_material': [
                {'name': 'Iron Ore', 'base_cost': 15, 'market_price': 20},
                {'name': 'Oil', 'base_cost': 25, 'market_price': 35},
                {'name': 'Wood', 'base_cost': 10, 'market_price': 15},
                {'name': 'Coal', 'base_cost': 12, 'market_price': 18},
                {'name': 'Copper', 'base_cost': 18, 'market_price': 25}
            ],
            'manufacturing': [
                {'name': 'Car Parts', 'base_cost': 45, 'market_price': 65},
                {'name': 'Electronics', 'base_cost': 55, 'market_price': 80},
                {'name': 'Furniture', 'base_cost': 35, 'market_price': 55},
                {'name': 'Tools', 'base_cost': 30, 'market_price': 45},
                {'name': 'Machinery', 'base_cost': 85, 'market_price': 120}
            ],
            'retail': [
                {'name': 'Consumer Goods', 'base_cost': 20, 'market_price': 35},
                {'name': 'Clothing', 'base_cost': 15, 'market_price': 30},
                {'name': 'Food Products', 'base_cost': 8, 'market_price': 15},
                {'name': 'Home Supplies', 'base_cost': 12, 'market_price': 22}
            ]
        }
        
        available_products = sector_products.get(company.sector, [])
        if not available_products:
            return []
        
        # Distribute production among available products
        products_to_create = random.sample(available_products, min(len(available_products), 3))
        
        for product_info in products_to_create:
            # Check if product already exists for this company
            existing_product = Product.query.filter_by(
                name=product_info['name'],
                company_id=company.id
            ).first()
            
            if existing_product:
                # Add to existing stock
                quantity_produced = production_amount // len(products_to_create)
                existing_product.stock_quantity += quantity_produced
                products_created.append({
                    'name': existing_product.name,
                    'quantity': quantity_produced,
                    'action': 'added_stock'
                })
            else:
                # Create new product
                quantity_produced = production_amount // len(products_to_create)
                new_product = Product(
                    name=product_info['name'],
                    category=company.sector,
                    base_cost=product_info['base_cost'],
                    market_price=product_info['market_price'],
                    stock_quantity=quantity_produced,
                    company_id=company.id
                )
                db.session.add(new_product)
                products_created.append({
                    'name': new_product.name,
                    'quantity': quantity_produced,
                    'action': 'created_new'
                })
        
        return products_created
    
    @staticmethod
    def calculate_production_costs(company, production_amount):
        """Calculate the costs of production"""
        if production_amount <= 0:
            return 0
        
        # Base cost per unit produced
        base_cost_per_unit = {
            'raw_material': 8,
            'manufacturing': 25,
            'retail': 12
        }
        
        unit_cost = base_cost_per_unit.get(company.sector, 15)
        
        # Employee salaries (already calculated separately)
        # Material costs
        material_costs = production_amount * unit_cost
        
        # Overhead costs (10% of material costs)
        overhead_costs = material_costs * 0.1
        
        return material_costs + overhead_costs
    
    @staticmethod
    def process_all_companies():
        """Process production for all companies with employees"""
        companies = Company.query.all()
        production_results = []
        
        for company in companies:
            if company.employees.count() > 0:
                result = ProductionEngine.process_company_production(company)
                production_results.append(result)
                
                # Broadcast company production event
                if result['production'] > 0:
                    from app.socketio_events import broadcast_company_event
                    broadcast_company_event({
                        'type': 'production',
                        'company_name': company.name,
                        'message': f"Produced {result['production']} units with {result['efficiency']:.1%} efficiency"
                    })
        
        return production_results
    
    @staticmethod
    def get_production_report(company):
        """Get detailed production report for a company"""
        if not company.employees.count():
            return {
                'status': 'inactive',
                'message': 'No employees - production stopped'
            }
        
        capacity = ProductionEngine.calculate_production_capacity(company)
        efficiency = ProductionEngine.calculate_efficiency(company)
        potential_production = int(capacity * efficiency)
        production_costs = ProductionEngine.calculate_production_costs(company, potential_production)
        
        return {
            'status': 'active',
            'capacity': capacity,
            'efficiency': efficiency,
            'potential_production': potential_production,
            'production_costs': production_costs,
            'employee_count': company.employees.count(),
            'cash_available': company.cash,
            'can_afford_production': company.cash >= production_costs
        }