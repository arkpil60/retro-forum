from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services.auth_service import AuthService
from datetime import datetime # <- ДОБАВИЛИ ИМПОРТ ВРЕМЕНИ

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html', current_time=datetime.now())
        
    username = request.form.get('username')
    password = request.form.get('password')
    
    result = AuthService.register_user(username, password)
    
    if result['success']:
        return redirect('/login')
    else:
        return render_template('auth/register.html', error=result['message'], current_time=datetime.now())


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html', current_time=datetime.now())
        
    username = request.form.get('username')
    password = request.form.get('password')
    
    result = AuthService.login_user(username, password)
    
    if result['success']:
        session['user_id'] = result['user_id']
        session['username'] = result['username']
        return redirect('/')
    else:
        return render_template('auth/login.html', error=result['message'], current_time=datetime.now())


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
