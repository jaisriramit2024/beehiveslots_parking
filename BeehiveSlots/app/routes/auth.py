from flask import Blueprint, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/owner', methods=['GET', 'POST'])
def register_owner():
    # Already logged in? Go straight to dashboard
    if 'user_id' in session:
        if session.get('role') == 'Owner':
            return redirect('/owner_dashboard')
        return redirect('/driver_dashboard')
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']  # 'Owner' expected
        password = request.form.get('password', name)  # fallback to name for backward compat

        if User.query.filter_by(name=name).first():
            flash('That username is already taken, try another!')
            return redirect('/register/owner')

        password_hash = generate_password_hash(password)
        new_user = User(name=name, role=role, password_hash=password_hash, wallet_balance=0)
        db.session.add(new_user)
        db.session.commit()

        # Auto-login: set session immediately so they land on the dashboard
        session['user_id'] = new_user.id
        session['name'] = new_user.name
        session['role'] = new_user.role
        session['wallet'] = new_user.wallet_balance

        flash("🎉 Account created! Now add your first parking space below.")
        return redirect('/owner_dashboard')

    return render_template('register_owner.html')

@auth_bp.route('/register/parker', methods=['GET', 'POST'])
def register_parker():
    if 'user_id' in session:
        if session.get('role') == 'Owner':
            return redirect('/owner_dashboard')
        return redirect('/driver_dashboard')
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role'] # 'Driver' expected
        
        if User.query.filter_by(name=name).first():
            flash('That username is already taken, try another!')
            return redirect('/register/parker')
            
        password_hash = generate_password_hash(name) 
        balance = 500 # Free credits for drivers
        
        new_user = User(name=name, role=role, password_hash=password_hash, wallet_balance=balance)
        db.session.add(new_user)
        db.session.commit()

        # Auto-login: set session immediately
        session['user_id'] = new_user.id
        session['name'] = new_user.name
        session['role'] = new_user.role
        session['wallet'] = new_user.wallet_balance
        
        flash("🎉 Welcome! You have ₹500 free credits. Search for parking below.")
        return redirect('/driver_dashboard')
        
    return render_template('register_parker.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'Owner':
            return redirect('/owner_dashboard')
        return redirect('/driver_dashboard')
    if request.method == 'POST':
        name = request.form['name']
        password = request.form.get('password', name)  # fallback for legacy accounts

        user = User.query.filter_by(name=name).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['name'] = user.name
            session['role'] = user.role
            session['wallet'] = user.wallet_balance

            if user.role == 'Owner':
                return redirect('/owner_dashboard')
            else:
                return redirect('/driver_dashboard')
        else:
            flash("Hmm, we don't recognize those details. Please try again.")

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect('/')
