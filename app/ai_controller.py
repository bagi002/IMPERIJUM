"""
AI Player Controller for IMPERIJUM
Manages AI decision making and automated gameplay
"""

from app import db
from app.models import User, Company, Product, Market, Worker, Employee, GameState, StockHolding, Loan
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AIPlayer:
    """AI Player decision-making controller"""
    
    def __init__(self, user):
        self.user = user
        self.personality = self._determine_personality()
        self.risk_tolerance = random.uniform(0.2, 0.8)  # 0 = conservative, 1 = aggressive
    
    def _determine_personality(self):
        """Determine AI personality type for decision making"""
        personalities = [
            'conservative',  # Safe investments, slow growth
            'aggressive',    # High-risk, high-reward
            'balanced',      # Mix of safe and risky moves
            'opportunistic', # Reacts quickly to market changes
            'growth',        # Focuses on expansion
            'value'          # Looks for undervalued assets
        ]
        return random.choice(personalities)
    
    def make_turn_decisions(self):
        """Make all decisions for this AI player's turn"""
        try:
            decisions = []
            
            # 1. Evaluate current financial position
            self._evaluate_position()
            
            # 2. Respond to recent market events
            market_response = self._respond_to_market_events()
            decisions.extend(market_response)
            
            # 3. Make company decisions
            for company in self.user.companies:
                company_decisions = self._make_company_decisions(company)
                decisions.extend(company_decisions)
            
            # 4. Make investment decisions based on personality
            investment_decisions = self._make_investment_decisions()
            decisions.extend(investment_decisions)
            
            # 5. Make hiring decisions
            hiring_decisions = self._make_hiring_decisions()
            decisions.extend(hiring_decisions)
            
            # 6. Consider creating new company based on market conditions
            if len(self.user.companies) < 3 and self.user.cash > 50000:
                new_company_decision = self._consider_new_company()
                if new_company_decision:
                    decisions.append(new_company_decision)
            
            # 7. Consider loans if cash is low or opportunities exist
            loan_decision = self._evaluate_loan_opportunities()
            if loan_decision:
                decisions.append(loan_decision)
            
            # 8. Make strategic decisions based on personality
            strategic_decisions = self._make_strategic_decisions()
            decisions.extend(strategic_decisions)
            
            logger.info(f"AI Player {self.user.username} ({self.personality}) made {len(decisions)} decisions")
            return decisions
            
        except Exception as e:
            logger.error(f"Error in AI decision making for {self.user.username}: {e}")
            return []
    
    def _evaluate_position(self):
        """Evaluate current financial and market position"""
        self.cash = self.user.cash
        self.net_worth = self.user.get_net_worth()
        self.company_count = len(self.user.companies)
        self.debt_level = sum([loan.remaining_amount for loan in self.user.loans])
    
    def _make_investment_decisions(self):
        """Make stock investment decisions"""
        decisions = []
        
        # Only invest if we have sufficient cash
        if self.user.cash < 20000:
            return decisions
        
        # Get available stocks
        available_companies = Company.query.filter(Company.available_shares > 0).all()
        
        # Filter out own companies
        available_companies = [c for c in available_companies if c.owner_id != self.user.id]
        
        if not available_companies:
            return decisions
        
        # Investment strategy based on personality
        investment_budget = self.user.cash * 0.1  # Invest up to 10% of cash
        
        if self.personality == 'value':
            # Look for undervalued companies
            sorted_companies = sorted(available_companies, key=lambda c: c.stock_price)
            target_company = sorted_companies[0] if sorted_companies else None
        elif self.personality == 'growth':
            # Look for companies with good revenue
            sorted_companies = sorted(available_companies, key=lambda c: c.monthly_revenue, reverse=True)
            target_company = sorted_companies[0] if sorted_companies else None
        else:
            # Random selection for other personalities
            target_company = random.choice(available_companies)
        
        if target_company and target_company.stock_price > 0:
            max_shares = min(
                int(investment_budget / target_company.stock_price),
                target_company.available_shares
            )
            
            if max_shares > 0:
                shares_to_buy = random.randint(1, max_shares)
                total_cost = shares_to_buy * target_company.stock_price
                
                # Create stock holding
                holding = StockHolding.query.filter_by(
                    user_id=self.user.id,
                    company_id=target_company.id
                ).first()
                
                if holding:
                    # Update existing holding
                    avg_price = (holding.shares * holding.purchase_price + shares_to_buy * target_company.stock_price) / (holding.shares + shares_to_buy)
                    holding.shares += shares_to_buy
                    holding.purchase_price = avg_price
                else:
                    # Create new holding
                    holding = StockHolding(
                        user_id=self.user.id,
                        company_id=target_company.id,
                        shares=shares_to_buy,
                        purchase_price=target_company.stock_price
                    )
                    db.session.add(holding)
                
                self.user.cash -= total_cost
                target_company.available_shares -= shares_to_buy
                target_company.cash += total_cost
                
                decisions.append(f"Bought {shares_to_buy} shares of {target_company.name} for ${total_cost:.2f}")
        
        return decisions
    
    def _make_hiring_decisions(self):
        """Make hiring decisions"""
        decisions = []
        
        # Only hire if companies are profitable
        for company in self.user.companies:
            if company.get_monthly_profit() > 5000 and company.employees.count() < 5:
                # Look for workers matching company sector
                sector_specializations = {
                    'raw_materials': ['mining', 'general'],
                    'manufacturing': ['manufacturing', 'technical', 'general'],
                    'retail': ['retail', 'general']
                }
                
                preferred_specs = sector_specializations.get(company.sector, ['general'])
                
                available_workers = Worker.query.filter_by(is_employed=False).filter(
                    Worker.specialization.in_(preferred_specs)
                ).limit(5).all()
                
                if available_workers:
                    # Hire the best worker we can afford
                    affordable_workers = [w for w in available_workers if w.desired_salary < company.cash * 0.1]
                    
                    if affordable_workers:
                        # Sort by skill level (expert > skilled > basic)
                        skill_order = {'expert': 3, 'skilled': 2, 'basic': 1}
                        best_worker = max(affordable_workers, key=lambda w: skill_order.get(w.skill_level, 0))
                        
                        # Offer slightly above desired salary to ensure hiring
                        salary_offer = best_worker.desired_salary * 1.1
                        
                        employee = Employee(
                            worker_id=best_worker.id,
                            company_id=company.id,
                            salary=salary_offer
                        )
                        
                        best_worker.is_employed = True
                        db.session.add(employee)
                        
                        decisions.append(f"Hired {best_worker.name} ({best_worker.skill_level}) for {company.name} at ${salary_offer:.0f}")
        
        return decisions
    
    def _consider_new_company(self):
        """Consider creating a new company"""
        if random.random() > 0.3:  # 30% chance to create new company
            return None
        
        sectors = ['raw_materials', 'manufacturing', 'retail']
        chosen_sector = random.choice(sectors)
        
        # Investment amount based on personality
        if self.personality == 'conservative':
            investment = min(self.user.cash * 0.2, 25000)
        elif self.personality == 'aggressive':
            investment = min(self.user.cash * 0.5, 100000)
        else:
            investment = min(self.user.cash * 0.3, 50000)
        
        if investment < 5000:
            return None
        
        # Generate company name
        sector_names = {
            'raw_materials': ['Mining Corp', 'Resources Ltd', 'Materials Inc', 'Extract Co'],
            'manufacturing': ['Industries Inc', 'Manufacturing Ltd', 'Factory Corp', 'Production Co'],
            'retail': ['Retail Group', 'Store Corp', 'Market Inc', 'Sales Ltd']
        }
        
        base_name = random.choice(sector_names[chosen_sector])
        company_name = f"{self.user.username} {base_name}"
        
        # Check if name exists
        existing = Company.query.filter_by(name=company_name).first()
        if existing:
            company_name = f"{company_name} {random.randint(1, 999)}"
        
        company = Company(
            name=company_name,
            sector=chosen_sector,
            owner_id=self.user.id,
            cash=investment
        )
        
        self.user.cash -= investment
        db.session.add(company)
        
        return f"Created new company: {company_name} ({chosen_sector}) with ${investment:.0f} investment"
    
    def _consider_loan(self):
        """Consider taking a loan"""
        if random.random() > 0.4:  # 40% chance to take loan when cash is low
            return None
        
        # Determine loan amount based on net worth
        max_loan = min(self.net_worth * 0.5, 100000)
        if max_loan < 5000:
            return None
        
        loan_amount = random.uniform(5000, max_loan)
        duration = random.choice([12, 24, 36])
        
        # Calculate terms
        base_rate = 0.05
        interest_rate = base_rate + random.uniform(0, 0.03)
        monthly_rate = interest_rate / 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** duration) / \
                         ((1 + monthly_rate) ** duration - 1)
        
        loan = Loan(
            user_id=self.user.id,
            amount=loan_amount,
            interest_rate=interest_rate,
            monthly_payment=monthly_payment,
            remaining_amount=loan_amount,
            months_remaining=duration
        )
        
        self.user.cash += loan_amount
        db.session.add(loan)
        
        return f"Took personal loan of ${loan_amount:.0f} at {interest_rate*100:.1f}% for {duration} months"

    def _respond_to_market_events(self):
        """Respond to recent market events based on personality"""
        decisions = []
        
        # This would normally check a market events log
        # For now, simulate responses to market conditions
        
        # Get current market conditions
        products = Product.query.all()
        volatile_products = [p for p in products if abs(random.uniform(-0.1, 0.1)) > 0.05]
        
        for product in volatile_products[:2]:  # Respond to up to 2 market changes
            if self.personality == 'opportunistic':
                # Opportunistic AI reacts quickly to price changes
                if product.get_demand_level() == 'Very High':
                    decisions.append(f"Opportunistic response: Increasing focus on {product.name} due to high demand")
            elif self.personality == 'conservative':
                # Conservative AI avoids volatile markets
                decisions.append(f"Conservative response: Reducing exposure to volatile {product.name} market")
            elif self.personality == 'aggressive':
                # Aggressive AI takes bigger risks during volatility
                decisions.append(f"Aggressive response: Doubling down on {product.name} volatility")
        
        return decisions

    def _make_strategic_decisions(self):
        """Make personality-based strategic decisions"""
        decisions = []
        
        if self.personality == 'growth':
            # Growth personality focuses on expansion
            if self.user.cash > 30000 and len(self.user.companies) < 3:
                decisions.append("Growth strategy: Preparing for aggressive expansion")
            
        elif self.personality == 'value':
            # Value personality looks for undervalued assets
            undervalued_stocks = Company.query.filter(
                Company.stock_price < Company.cash / 100
            ).limit(3).all()
            
            if undervalued_stocks:
                decisions.append(f"Value strategy: Identified {len(undervalued_stocks)} undervalued investment opportunities")
        
        elif self.personality == 'balanced':
            # Balanced personality maintains diversification
            sectors = set([c.sector for c in self.user.companies])
            if len(sectors) < 2 and len(self.user.companies) >= 2:
                decisions.append("Balanced strategy: Need to diversify across different sectors")
        
        return decisions

    def _evaluate_loan_opportunities(self):
        """Enhanced loan evaluation based on opportunities"""
        # Check if cash is low
        if self.user.cash < 10000:
            return self._consider_loan()
        
        # Consider loan for growth opportunities (growth and aggressive personalities)
        if self.personality in ['growth', 'aggressive'] and self.user.cash < 50000:
            if len(self.user.companies) < 2:  # Opportunity to expand
                if random.random() < 0.3:  # 30% chance
                    loan_amount = random.uniform(20000, 50000)
                    return f"Strategic loan of ${loan_amount:.0f} for expansion opportunity"
        
        return None

    def _make_company_decisions(self, company):
        """Enhanced company decision making"""
        decisions = []
        
        # Production decisions based on market conditions and personality
        if company.cash > 5000:
            for product in company.products:
                demand_level = product.get_demand_level()
                
                # Personality-based production decisions
                if self.personality == 'aggressive' and demand_level in ['High', 'Very High']:
                    # Aggressive AI increases production more when demand is high
                    production_increase = 30
                elif self.personality == 'conservative' and demand_level in ['Moderate', 'High']:
                    # Conservative AI only increases production moderately
                    production_increase = 15
                elif self.personality == 'opportunistic' and demand_level == 'Very High':
                    # Opportunistic AI maximizes high-demand situations
                    production_increase = 40
                else:
                    production_increase = 20  # Default
                
                if product.stock_quantity < 50 and demand_level in ['High', 'Very High']:
                    production_cost = product.base_cost * production_increase
                    if company.cash >= production_cost:
                        product.stock_quantity += production_increase
                        company.cash -= production_cost
                        decisions.append(f"Increased production of {product.name} by {production_increase} units")
        
        # Enhanced pricing decisions
        for product in company.products:
            demand_level = product.get_demand_level()
            market_price = product.market_price
            
            # More sophisticated pricing based on personality
            if self.personality == 'aggressive':
                # Aggressive pricing - push prices higher
                if demand_level == 'Very High':
                    new_price = min(market_price * 1.25, product.market_price * 1.4)
                    if hasattr(product, 'selling_price'):
                        old_price = product.selling_price
                        product.selling_price = new_price
                        decisions.append(f"Aggressive pricing: Raised {product.name} to ${new_price:.2f}")
                        
            elif self.personality == 'value':
                # Value pricing - competitive but profitable
                if demand_level == 'Low':
                    new_price = max(market_price * 0.9, product.base_cost * 1.15)
                    if hasattr(product, 'selling_price'):
                        old_price = product.selling_price
                        product.selling_price = new_price
                        decisions.append(f"Value pricing: Competitive price for {product.name} at ${new_price:.2f}")
        
        return decisions


class AIController:
    """Controller for managing all AI players"""
    
    @staticmethod
    def process_ai_turns():
        """Process turns for all AI players"""
        ai_players = User.query.filter_by(is_ai=True).all()
        all_decisions = {}
        
        for ai_user in ai_players:
            ai_player = AIPlayer(ai_user)
            decisions = ai_player.make_turn_decisions()
            all_decisions[ai_user.username] = decisions
        
        db.session.commit()
        return all_decisions
    
    @staticmethod
    def create_ai_player(name=None, difficulty='medium'):
        """Create a new AI player"""
        if not name:
            name = f"AI_Player_{random.randint(1000, 9999)}"
        
        # Ensure unique name
        existing = User.query.filter_by(username=name).first()
        if existing:
            name = f"{name}_{random.randint(100, 999)}"
        
        # Difficulty affects starting resources
        if difficulty == 'easy':
            starting_cash = random.randint(50000, 80000)
        elif difficulty == 'hard':
            starting_cash = random.randint(120000, 200000)
        else:  # medium
            starting_cash = random.randint(80000, 120000)
        
        ai_user = User(
            username=name,
            email=f"{name.lower()}@ai.imperijum",
            cash=starting_cash,
            is_ai=True
        )
        ai_user.set_password('ai_password')  # AI players don't log in
        
        db.session.add(ai_user)
        db.session.commit()
        
        return ai_user