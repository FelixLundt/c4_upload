from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.config import Config

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        group_id = request.form['group_id']
        password = request.form['password']
        
        if group_id in Config.ALLOWED_GROUPS:
            if password == Config.ALLOWED_GROUPS[group_id]['password']:
                session['group_id'] = group_id
                session['group_name'] = Config.ALLOWED_GROUPS[group_id]['name']
                return redirect(url_for('upload.upload'))
            else:
                flash('Invalid password')
        else:
            flash('Invalid group ID')
            
        return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.method == 'GET':
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('auth.login'))
    return '', 204  # No content response for POST/beacon requests
