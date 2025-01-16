from flask import Blueprint, render_template, session

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    """Landing page route"""
    return render_template('home.html')