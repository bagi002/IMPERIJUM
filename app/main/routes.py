from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.main import bp
from app.models import User, GameState

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('game.dashboard'))
    return render_template('index.html')

@bp.route('/leaderboard')
def leaderboard():
    players = User.query.filter_by(is_ai=False).order_by(User.cash.desc()).limit(10).all()
    return render_template('leaderboard.html', players=players)