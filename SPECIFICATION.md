# IMPERIJUM - Economic Simulation Game
## Detailed Technical Specification

### 1. Project Overview
IMPERIJUM is a web-based economic simulation game where players manage companies across three business sectors, compete with AI opponents, and engage in a dynamic market economy.

### 2. Core Game Mechanics

#### 2.1 Player System
- **Registration**: Players start with configurable initial capital (default: $100,000)
- **AI Players**: Computer-controlled opponents with automated decision-making
- **Authentication**: Secure login/logout with session management
- **User Profiles**: Track cash, net worth, companies owned, stock holdings

#### 2.2 Company Management System
- **Three Business Sectors**:
  - **Raw Materials**: Extract and produce basic resources (iron, oil, wood, etc.)
  - **Manufacturing**: Process raw materials into finished goods
  - **Retail**: Sell products directly to consumers

- **Company Attributes**:
  - Name, sector, cash reserves, stock price
  - Reputation (affects sales and pricing power)
  - Monthly revenue/expenses tracking
  - Employee count and productivity

#### 2.3 Economic System
- **Dynamic Pricing**: Market prices fluctuate based on supply and demand
- **Product Trading**: Buy/sell between companies and on public market
- **Supply Chain**: Raw materials → Manufacturing → Retail flow
- **Market Volatility**: Configurable price fluctuation percentage

#### 2.4 Workforce Management
- **Worker Pool**: Available workers with different skill levels and specializations
- **Hiring System**: Workers go to highest bidder
- **Salary Competition**: Players must offer competitive wages
- **Skill Categories**: Basic, Skilled, Expert workers
- **Specializations**: General, Manufacturing, Retail, Mining, etc.

#### 2.5 Stock Exchange
- **Company Shares**: Companies can sell partial ownership
- **Stock Trading**: Buy/sell shares between players
- **Market Valuation**: Stock prices based on company performance
- **Dividend System**: Share profits with stockholders

#### 2.6 Banking System
- **Loans**: Players and companies can borrow money
- **Interest Rates**: Configurable lending rates
- **Credit Ratings**: Based on payment history and company performance
- **Monthly Payments**: Automatic loan servicing

#### 2.7 Turn-Based System
- **Turn Progression**: Game advances when all players confirm ready
- **AI Automation**: AI players make decisions automatically
- **Time Limits**: Optional turn time limits
- **Game State Tracking**: Current turn, player readiness

### 3. Technical Architecture

#### 3.1 Backend (Flask)
```
app/
├── __init__.py          # Flask app factory
├── models.py            # SQLAlchemy database models
├── auth/                # Authentication blueprint
├── main/                # Main site pages
├── game/                # Game mechanics
├── api/                 # JSON API endpoints
├── templates/           # Jinja2 HTML templates
└── static/              # CSS, JavaScript, images
```

#### 3.2 Database Schema
**Core Tables**:
- `users` - Player accounts and AI entities
- `companies` - Business entities owned by players
- `products` - Items produced/traded in market
- `workers` - Available workforce pool
- `employees` - Worker-company assignments
- `market` - Transaction history
- `stock_holdings` - Share ownership tracking
- `loans` - Credit and debt tracking
- `game_state` - Global game status

#### 3.3 Frontend
- **Bootstrap 5**: Responsive CSS framework
- **Vanilla JavaScript**: Real-time updates via AJAX
- **WebSocket Support**: For live notifications (Flask-SocketIO)
- **Mobile Responsive**: Works on tablets and phones

### 4. API Endpoints

#### 4.1 Game Data APIs
- `GET /api/companies` - User's company information
- `GET /api/market_data` - Current market prices and inventory
- `GET /api/game_state` - Current turn and player status
- `GET /api/player_stats` - Current player statistics

#### 4.2 Game Action APIs
- `POST /game/create_company` - Start new business
- `POST /game/hire_worker` - Employ workforce
- `POST /game/buy_stock` - Purchase company shares
- `POST /game/buy_product` - Market transactions
- `POST /game/next_turn` - Signal ready for turn advance

### 5. Game Balance Configuration

#### 5.1 Economic Parameters
```python
INITIAL_PLAYER_CAPITAL = 100000
BASE_WORKER_SALARY = 1000
MARKET_VOLATILITY = 0.1
STOCK_TRADING_FEE = 0.01
TURN_DURATION = 300  # seconds
```

#### 5.2 Scaling Factors
- **Company Valuation**: Based on cash + assets + revenue multiplier
- **Worker Productivity**: Skill level affects output
- **Market Demand**: Seasonal and random fluctuations
- **AI Difficulty**: Adjustable decision-making intelligence

### 6. Security Considerations
- **Input Validation**: All form data sanitized
- **Authentication**: Session-based login with CSRF protection
- **Rate Limiting**: Prevent API abuse
- **Data Integrity**: Transaction atomicity for financial operations

### 7. Performance Optimization
- **Database Indexing**: On foreign keys and frequently queried fields
- **Caching**: Market data and game state caching
- **Async Updates**: Background processing for AI moves
- **Pagination**: Large data sets split across pages

### 8. Testing Strategy
- **Unit Tests**: Model methods and business logic
- **Integration Tests**: API endpoint functionality
- **Game Logic Tests**: Turn processing and market mechanics
- **Load Testing**: Multiple concurrent players

### 9. Deployment Requirements
- **Development**: SQLite database, Flask dev server
- **Production**: PostgreSQL, Gunicorn, Nginx
- **Environment Variables**: Database URLs, secret keys
- **Static Assets**: CDN for CSS/JS libraries

### 10. Future Enhancements
- **Real-time Chat**: Player communication
- **Advanced Analytics**: Detailed performance charts
- **Seasonal Events**: Special market conditions
- **Company Mergers**: Advanced corporate actions
- **Technology Research**: Unlock new products/capabilities
- **International Markets**: Multiple economic regions