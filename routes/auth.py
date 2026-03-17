from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
from werkzeug.security import check_password_hash
from database.models import User, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('home.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if user.role == 'admin':
                flash('Admin Dashboard Access Granted!', 'success')
                return redirect(next_page or url_for('admin.index'))
            elif user.role == 'student':  # user.role == 'student'
                flash('Welcome to Student Dashboard!', 'success')
                return redirect(next_page or url_for('dashboard.index'))
            else:
                logout_user()
                flash('Invalid user role. Contact admin.', 'error')
                return redirect(url_for('auth.login'))
        flash('Invalid email or password.', 'error')
    return render_template('auth/login.html')



@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/signup.html')
        
        user = User(
            email=email,
            name=name,
            role='student',
            is_admin=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Account created! Start by adding a subject.', 'success')
        return redirect(url_for('subjects.index'))
    return render_template('auth/signup.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.home'))

