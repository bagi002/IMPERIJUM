"""
Market Engine for IMPERIJUM Economic Simulation
Handles price updates, company valuations, and market dynamics
"""

from app import db
from app.models import Product, Company, GameState
import random
from datetime import datetime


class MarketEngine:
    """Market simulation engine for economic calculations"""
    
    @staticmethod
    def update_all_prices():
        """Update all product prices based on supply and demand"""
        products = Product.query.all()
        price_changes = []
        
        for product in products:
            old_price = product.market_price
            new_price = product.update_market_price()
            change_percent = ((new_price - old_price) / old_price) * 100 if old_price > 0 else 0
            
            price_changes.append({
                'product': product.name,
                'old_price': old_price,
                'new_price': new_price,
                'change_percent': change_percent,
                'demand_level': product.get_demand_level()
            })
        
        db.session.commit()
        return price_changes
    
    @staticmethod
    def update_company_valuations():
        """Update all company stock prices based on valuation"""
        companies = Company.query.all()
        valuation_changes = []
        
        for company in companies:
            old_price = company.stock_price
            new_price = company.update_stock_price()
            change_percent = ((new_price - old_price) / old_price) * 100 if old_price > 0 else 0
            
            valuation_changes.append({
                'company': company.name,
                'old_price': old_price,
                'new_price': new_price,
                'change_percent': change_percent,
                'valuation': company.calculate_valuation()
            })
        
        db.session.commit()
        return valuation_changes
    
    @staticmethod
    def simulate_ai_demand():
        """Simulate market demand from AI players and NPCs"""
        products = Product.query.all()
        
        for product in products:
            # Simulate random demand fluctuations
            base_demand = 50 + random.randint(-20, 30)
            
            # Adjust demand based on category
            if product.category == 'raw_material':
                demand_multiplier = 1.2  # Higher demand for raw materials
            elif product.category == 'manufactured':
                demand_multiplier = 1.0
            else:  # retail
                demand_multiplier = 0.8
            
            # Price sensitivity - higher prices reduce demand
            price_sensitivity = max(0.3, 1.0 - (product.market_price / (product.base_cost * 2)))
            
            new_demand = int(base_demand * demand_multiplier * price_sensitivity)
            product.monthly_demand = max(new_demand, 10)  # Minimum demand
        
        db.session.commit()
    
    @staticmethod
    def process_turn():
        """Process a complete economic turn"""
        # 1. Simulate AI demand
        MarketEngine.simulate_ai_demand()
        
        # 2. Update product prices
        price_changes = MarketEngine.update_all_prices()
        
        # 3. Update company valuations
        valuation_changes = MarketEngine.update_company_valuations()
        
        # 4. Update companies' monthly performance
        MarketEngine.update_company_performance()
        
        return {
            'price_changes': price_changes,
            'valuation_changes': valuation_changes,
            'timestamp': datetime.utcnow()
        }
    
    @staticmethod
    def update_company_performance():
        """Update monthly performance metrics for companies"""
        companies = Company.query.all()
        
        for company in companies:
            # Calculate revenue based on products sold
            revenue = 0
            for product in company.products:
                # Simulate sales based on demand and stock
                potential_sales = min(product.stock_quantity, product.monthly_demand // 4)  # Weekly sales
                sales_revenue = potential_sales * product.selling_price
                revenue += sales_revenue
                
                # Reduce stock
                product.stock_quantity = max(0, product.stock_quantity - potential_sales)
            
            # Calculate expenses (employee salaries)
            expenses = sum([emp.salary for emp in company.employees])
            
            # Update company financials
            company.monthly_revenue = revenue
            company.monthly_expenses = expenses
            company.cash += (revenue - expenses)
            
            # Update reputation based on performance
            profit_margin = (revenue - expenses) / max(revenue, 1)
            if profit_margin > 0.2:
                company.reputation = min(100, company.reputation + 2)
            elif profit_margin < -0.1:
                company.reputation = max(0, company.reputation - 3)
        
        db.session.commit()
    
    @staticmethod
    def get_market_summary():
        """Get comprehensive market summary"""
        products = Product.query.all()
        companies = Company.query.all()
        
        # Calculate market metrics
        total_market_cap = sum([c.get_company_value() for c in companies])
        avg_stock_price = sum([c.stock_price for c in companies]) / len(companies) if companies else 0
        
        # Product metrics
        total_products = len(products)
        avg_price = sum([p.market_price for p in products]) / len(products) if products else 0
        
        # Demand levels
        high_demand_products = [p for p in products if p.get_demand_level() in ['High', 'Very High']]
        
        return {
            'total_companies': len(companies),
            'total_market_cap': total_market_cap,
            'avg_stock_price': avg_stock_price,
            'total_products': total_products,
            'avg_product_price': avg_price,
            'high_demand_products': len(high_demand_products),
            'market_activity': 'Active' if len(high_demand_products) > total_products * 0.3 else 'Moderate'
        }