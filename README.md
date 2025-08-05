# IMPERIJUM - Economic Simulation Game

A sophisticated web-based economic simulation game where players build business empires, manage resources, and compete in dynamic markets.

![Homepage](https://github.com/user-attachments/assets/095d55cc-b035-47af-90f9-46b51b517d79)

## 🎮 Game Features

- **Multi-player Economy**: Real-time economic simulation with human and AI players
- **Three Business Sectors**: Raw materials, manufacturing, and retail companies
- **Dynamic Markets**: Supply and demand-based pricing with market volatility
- **Workforce Management**: Hire workers with different skills and specializations
- **Stock Exchange**: Trade company shares and build investment portfolios
- **Banking System**: Loans and credit for business expansion
- **Turn-based Strategy**: Strategic gameplay with coordinated turn progression

![Leaderboard](https://github.com/user-attachments/assets/c1523c07-f519-4967-85a5-506197d62239)

## 🏗️ Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLAlchemy with SQLite (development) / PostgreSQL (production)
- **Real-time**: WebSocket support via Flask-SocketIO
- **Authentication**: Flask-Login with secure session management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bagi002/IMPERIJUM.git
   cd IMPERIJUM
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python init_db.py
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🎯 How to Play

1. **Register** and receive starting capital ($100,000)
2. **Create companies** in any of the three sectors:
   - **Raw Materials**: Extract and produce basic resources
   - **Manufacturing**: Process raw materials into finished goods  
   - **Retail**: Sell products directly to consumers
3. **Hire workers** with different skills and specializations
4. **Trade products** on the dynamic market
5. **Invest in stocks** and manage your portfolio
6. **Expand your empire** and compete to become the richest player!

## 🏢 Game Mechanics

### Company Sectors
- **Raw Materials**: Iron ore, oil, wood, coal, copper, aluminum, gold
- **Manufacturing**: Car parts, electronics, furniture, tools, machinery
- **Retail**: Consumer goods, clothing, food, home supplies

### Economic System
- **Supply & Demand**: Prices fluctuate based on market activity
- **Market Volatility**: Configurable price variation (default: 10%)
- **Cross-sector Trading**: Raw materials → Manufacturing → Retail

### Workforce
- **Skill Levels**: Basic, Skilled, Expert workers
- **Specializations**: General, Manufacturing, Retail, Mining, Technical
- **Competitive Hiring**: Workers join the highest bidder

## 🛠️ Development

### Project Structure
```
IMPERIJUM/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models.py            # Database models
│   ├── auth/               # Authentication blueprint
│   ├── main/               # Main site pages
│   ├── game/               # Game mechanics
│   ├── api/                # JSON API endpoints
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JavaScript, images
├── config.py               # Configuration settings
├── run.py                 # Application entry point
├── init_db.py             # Database initialization
├── tests.py               # Unit tests
├── requirements.txt       # Python dependencies
├── SPECIFICATION.md       # Detailed technical specification
└── DEVELOPMENT_PLAN.md    # Development roadmap
```

### Running Tests
```bash
python tests.py
```

### API Endpoints
- `GET /api/companies` - User's company information
- `GET /api/market_data` - Current market prices and inventory
- `GET /api/game_state` - Current turn and player status
- `GET /api/player_stats` - Current player statistics

## 🔧 Configuration

Game settings can be adjusted in `config.py`:

```python
INITIAL_PLAYER_CAPITAL = 100000    # Starting money
BASE_WORKER_SALARY = 1000          # Minimum wage
MARKET_VOLATILITY = 0.1            # Price fluctuation
TURN_DURATION = 300                # Turn time limit (seconds)
MAX_PLAYERS = 20                   # Maximum human players
MAX_AI_PLAYERS = 10                # Maximum AI players
```

## 📊 Game Balance

### Economic Parameters
- **Starting Capital**: $100,000 per player
- **Company Creation**: Minimum $1,000 investment
- **Worker Salaries**: $1,000 - $3,000+ based on skill
- **Stock Trading Fee**: 1% of transaction value

### AI Behavior
- AI players make automated decisions each turn
- AI difficulty can be adjusted via company performance metrics
- AI players compete for workers and market share

## 🤝 Contributing

We welcome contributions! Please see our [Development Plan](DEVELOPMENT_PLAN.md) for details on:
- Parallel development tasks for multiple teams
- Code standards and testing requirements
- Integration milestones and deployment strategy

### Development Teams
1. **Backend Core**: Authentication, game logic, AI systems
2. **Economy Systems**: Market dynamics, company management, trading
3. **Frontend UI**: User interface, real-time updates, user experience

## 📚 Documentation

- [Technical Specification](SPECIFICATION.md) - Detailed game mechanics and architecture
- [Development Plan](DEVELOPMENT_PLAN.md) - Team tasks and project roadmap

## 🔐 Security

- CSRF protection on all forms
- Secure session management
- Input validation and sanitization
- Rate limiting on API endpoints

## 🚀 Deployment

### Development
```bash
python run.py  # Uses SQLite, Flask dev server
```

### Production
- Use PostgreSQL database
- Deploy with Gunicorn + Nginx
- Configure environment variables for secrets
- Use CDN for static assets

## 📈 Roadmap

### Phase 1 (Current) - Core MVP
- [x] User registration and authentication
- [x] Basic company creation and management
- [x] Market trading system
- [x] AI players with automated decisions
- [x] Leaderboard and player statistics

### Phase 2 - Enhanced Features
- [ ] Complete workforce management
- [ ] Stock exchange with real-time trading
- [ ] Banking and loan system
- [ ] Advanced AI strategies
- [ ] Real-time notifications

### Phase 3 - Advanced Systems
- [ ] Company mergers and acquisitions
- [ ] Technology research system
- [ ] Seasonal market events
- [ ] International markets
- [ ] Advanced analytics dashboard

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Flask and modern web technologies
- Inspired by classic economic simulation games
- Designed for multiplayer competitive gameplay

---

**Start your business empire today!** 🏭💰📈