import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///imperijum.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Game settings
    INITIAL_PLAYER_CAPITAL = 100000  # Starting money for new players
    TURN_DURATION = 300  # 5 minutes per turn in seconds
    MAX_PLAYERS = 20
    MAX_AI_PLAYERS = 10
    
    # Economic settings
    BASE_WORKER_SALARY = 1000
    MARKET_VOLATILITY = 0.1  # Price fluctuation percentage
    STOCK_TRADING_FEE = 0.01  # 1% trading fee

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}