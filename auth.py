from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, UserHistory, db, SavedArticle, VerificationResult, SearchQuery
import json
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
            
        # If validation passes, log in the user
        login_user(user, remember=remember)
        return redirect(url_for('index'))
        
    return render_template('auth/login.html', active_page='login')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))
            
        # Check if username already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('auth.signup'))
            
        # Create new user
        new_user = User(username=username, email=email, password=password)
        
        # Add user to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! You can now log in.')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/signup.html', active_page='signup')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@auth.route('/add_history', methods=['POST'])
@login_required
def add_history():
    try:
        data = request.get_json()
        action_type = data.get('action_type')
        action_details = data.get('action_details')
        article_url = data.get('article_url')
        article_title = data.get('article_title')
        
        if not action_type:
            return jsonify({'error': 'Action type is required'}), 400
        
        history_entry = UserHistory(
            user_id=current_user.id,
            action_type=action_type,
            action_details=action_details,
            article_url=article_url,
            article_title=article_title
        )
        
        db.session.add(history_entry)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'History added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth.route('/dashboard')
@login_required
def dashboard():
    # Get verification history
    verifications = VerificationResult.query.filter_by(user_id=current_user.id).order_by(VerificationResult.verified_at.desc()).all()
    
    # Get saved articles
    saved_articles = SavedArticle.query.filter_by(user_id=current_user.id).order_by(SavedArticle.saved_at.desc()).all()
    
    # Get search queries
    search_queries = SearchQuery.query.filter_by(user_id=current_user.id).order_by(SearchQuery.created_at.desc()).all()
    
    # Count statistics
    verification_count = len(verifications)
    saved_articles_count = len(saved_articles)
    search_queries_count = len(search_queries)
    
    return render_template('auth/dashboard.html',
                          active_page='dashboard',
                          verifications=verifications,
                          saved_articles=saved_articles,
                          search_queries=search_queries,
                          verification_count=verification_count,
                          saved_articles_count=saved_articles_count,
                          search_queries_count=search_queries_count)

@auth.route('/verification/<int:verification_id>')
@login_required
def verification_details(verification_id):
    # Get the verification result
    verification = VerificationResult.query.filter_by(id=verification_id, user_id=current_user.id).first_or_404()
    
    # Render the verification details template
    return render_template('auth/verification_details.html',
                          active_page='dashboard',
                          verification=verification)

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate username and email
        if username != current_user.username:
            user_exists = User.query.filter_by(username=username).first()
            if user_exists:
                flash('Username already exists')
                return redirect(url_for('auth.profile'))
        
        if email != current_user.email:
            email_exists = User.query.filter_by(email=email).first()
            if email_exists:
                flash('Email already exists')
                return redirect(url_for('auth.profile'))
        
        # Update password if provided
        if current_password and new_password and confirm_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect')
                return redirect(url_for('auth.profile'))
            
            if new_password != confirm_password:
                flash('New passwords do not match')
                return redirect(url_for('auth.profile'))
            
            current_user.set_password(new_password)
        
        # Update user information
        current_user.username = username
        current_user.email = email
        
        # Create history record for profile update
        history_entry = UserHistory(
            user_id=current_user.id,
            action_type='profile_updated',
            action_details=f'Profile updated on {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}')
        
        db.session.add(history_entry)
        db.session.commit()
        
        flash('Profile updated successfully')
        return redirect(url_for('auth.profile'))
    
    # Get user history
    user_history = UserHistory.query.filter_by(user_id=current_user.id).order_by(UserHistory.created_at.desc()).limit(10).all()
    
    # Count statistics
    verified_count = UserHistory.query.filter_by(user_id=current_user.id, action_type='article_verified').count()
    saved_count = UserHistory.query.filter_by(user_id=current_user.id, action_type='article_saved').count()
    total_contributions = UserHistory.query.filter_by(user_id=current_user.id).count()
    
    return render_template('auth/profile.html', 
                           active_page='profile', 
                           user_history=user_history,
                           verified_count=verified_count,
                           saved_count=saved_count,
                           total_contributions=total_contributions)
