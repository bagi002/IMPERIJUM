"""
Market Events System for IMPERIJUM
Generates random economic events that affect market conditions
"""

import random
from datetime import datetime
from app import db
from app.models import Product, Company, GameState
from app.socketio_events import broadcast_market_event

class MarketEvent:
    """Individual market event"""
    def __init__(self, event_type, title, description, affected_sectors, impact, effects):
        self.event_type = event_type
        self.title = title
        self.description = description
        self.affected_sectors = affected_sectors
        self.impact = impact  # 'positive', 'negative', 'neutral'
        self.effects = effects  # Dictionary of price multipliers or other effects

class MarketEventsEngine:
    """Manages random market events"""
    
    @staticmethod
    def get_random_event():
        """Generate a random market event"""
        events = [
            # Raw Materials Events
            MarketEvent(
                'supply_disruption',
                'Mining Strike Disrupts Supply',
                'A major mining workers\' strike has disrupted the supply of raw materials, causing prices to spike.',
                ['raw_material'],
                'negative',
                {'price_multiplier': 1.3, 'supply_reduction': 0.3}
            ),
            MarketEvent(
                'new_discovery',
                'Rich Mineral Deposits Discovered',
                'New mineral deposits have been discovered, increasing supply and reducing raw material costs.',
                ['raw_material'],
                'positive',
                {'price_multiplier': 0.8, 'supply_increase': 0.4}
            ),
            
            # Manufacturing Events
            MarketEvent(
                'tech_breakthrough',
                'Manufacturing Technology Breakthrough',
                'New manufacturing technology has increased efficiency, reducing production costs.',
                ['manufacturing'],
                'positive',
                {'price_multiplier': 0.9, 'productivity_boost': 0.2}
            ),
            MarketEvent(
                'factory_fire',
                'Major Factory Fire Causes Shortages',
                'A fire at a major manufacturing facility has caused product shortages across the sector.',
                ['manufacturing'],
                'negative',
                {'price_multiplier': 1.4, 'supply_reduction': 0.4}
            ),
            
            # Retail Events
            MarketEvent(
                'consumer_boom',
                'Consumer Spending Surge',
                'Economic optimism has led to increased consumer spending across all retail categories.',
                ['retail'],
                'positive',
                {'demand_multiplier': 1.3, 'price_multiplier': 1.1}
            ),
            MarketEvent(
                'recession_fears',
                'Economic Uncertainty Dampens Spending',
                'Fears of economic downturn have caused consumers to reduce spending on non-essential items.',
                ['retail'],
                'negative',
                {'demand_multiplier': 0.7, 'price_multiplier': 0.9}
            ),
            
            # Global Events
            MarketEvent(
                'trade_agreement',
                'New International Trade Agreement',
                'A new trade agreement has reduced tariffs and opened new markets for all sectors.',
                ['raw_material', 'manufacturing', 'retail'],
                'positive',
                {'demand_multiplier': 1.2, 'price_multiplier': 1.05}
            ),
            MarketEvent(
                'trade_war',
                'Trade War Escalates',
                'Rising trade tensions have led to increased tariffs and market uncertainty.',
                ['raw_material', 'manufacturing', 'retail'],
                'negative',
                {'demand_multiplier': 0.8, 'price_multiplier': 1.1}
            ),
            
            # Seasonal Events
            MarketEvent(
                'holiday_season',
                'Holiday Shopping Season Begins',
                'The holiday season has arrived, boosting demand for retail products.',
                ['retail'],
                'positive',
                {'demand_multiplier': 1.5, 'price_multiplier': 1.2}
            ),
            MarketEvent(
                'summer_slowdown',
                'Summer Business Slowdown',
                'Summer months typically see reduced business activity in manufacturing.',
                ['manufacturing'],
                'negative',
                {'demand_multiplier': 0.8, 'price_multiplier': 0.95}
            ),
            
            # Technology Events
            MarketEvent(
                'automation_boom',
                'Automation Revolution',
                'New automation technologies are changing the workforce landscape.',
                ['manufacturing'],
                'neutral',
                {'productivity_boost': 0.3, 'worker_demand_reduction': 0.2}
            ),
            MarketEvent(
                'cyber_attack',
                'Cyber Attack Disrupts Operations',
                'A major cyber attack has disrupted operations across multiple companies.',
                ['manufacturing', 'retail'],
                'negative',
                {'productivity_reduction': 0.3, 'recovery_time': 2}
            )
        ]
        
        return random.choice(events)
    
    @staticmethod
    def trigger_random_event():
        """Trigger a random market event with 15% probability"""
        if random.random() < 0.15:  # 15% chance per turn
            event = MarketEventsEngine.get_random_event()
            MarketEventsEngine.apply_event(event)
            return event
        return None
    
    @staticmethod
    def apply_event(event):
        """Apply the effects of a market event"""
        try:
            # Get products affected by this event
            affected_products = []
            if 'raw_material' in event.affected_sectors:
                affected_products.extend(Product.query.filter_by(category='raw_material').all())
            if 'manufacturing' in event.affected_sectors:
                affected_products.extend(Product.query.filter_by(category='manufactured').all())
            if 'retail' in event.affected_sectors:
                affected_products.extend(Product.query.filter_by(category='retail').all())
            
            # Apply price effects
            if 'price_multiplier' in event.effects:
                multiplier = event.effects['price_multiplier']
                for product in affected_products:
                    product.market_price *= multiplier
                    product.market_price = round(product.market_price, 2)
            
            # Apply demand effects
            if 'demand_multiplier' in event.effects:
                multiplier = event.effects['demand_multiplier']
                for product in affected_products:
                    if hasattr(product, 'monthly_demand'):
                        product.monthly_demand = int(product.monthly_demand * multiplier)
            
            # Apply supply effects
            if 'supply_reduction' in event.effects:
                reduction = event.effects['supply_reduction']
                for product in affected_products:
                    if product.stock_quantity:
                        product.stock_quantity = int(product.stock_quantity * (1 - reduction))
            
            if 'supply_increase' in event.effects:
                increase = event.effects['supply_increase']
                for product in affected_products:
                    if product.stock_quantity:
                        product.stock_quantity = int(product.stock_quantity * (1 + increase))
            
            # Save changes
            db.session.commit()
            
            # Broadcast event to all players
            broadcast_market_event({
                'type': event.event_type,
                'title': event.title,
                'description': event.description,
                'affected_sectors': event.affected_sectors,
                'impact': event.impact
            })
            
            print(f"Market event applied: {event.title}")
            
        except Exception as e:
            print(f"Error applying market event: {e}")
            db.session.rollback()
    
    @staticmethod
    def check_and_trigger_seasonal_events():
        """Check for and trigger seasonal events based on current date"""
        current_month = datetime.now().month
        
        # Holiday season (November-December)
        if current_month in [11, 12]:
            if random.random() < 0.3:  # 30% chance during holiday season
                event = MarketEvent(
                    'holiday_boost',
                    'Holiday Season Sales Boost',
                    'Holiday shopping is in full swing, increasing demand for all retail products.',
                    ['retail'],
                    'positive',
                    {'demand_multiplier': 1.4, 'price_multiplier': 1.15}
                )
                MarketEventsEngine.apply_event(event)
                return event
        
        # Summer slowdown (July-August)
        elif current_month in [7, 8]:
            if random.random() < 0.2:  # 20% chance during summer
                event = MarketEvent(
                    'summer_vacation',
                    'Summer Vacation Period',
                    'Many businesses slow down during summer vacation period.',
                    ['manufacturing'],
                    'negative',
                    {'demand_multiplier': 0.85, 'productivity_reduction': 0.15}
                )
                MarketEventsEngine.apply_event(event)
                return event
        
        return None