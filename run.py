from app import create_app, db
from app.models import User, Company, Product, Market, Worker, Employee, GameState, StockHolding, Loan

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Company': Company, 
        'Product': Product,
        'Market': Market,
        'Worker': Worker,
        'Employee': Employee,
        'GameState': GameState,
        'StockHolding': StockHolding,
        'Loan': Loan
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create initial game state if it doesn't exist
        if not GameState.query.first():
            game_state = GameState()
            db.session.add(game_state)
            db.session.commit()
    
    app.run(debug=True)