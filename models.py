from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(528), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    history = db.relationship('UserHistory', backref='user', lazy='dynamic')
    saved_articles = db.relationship('SavedArticle', backref='user', lazy='dynamic')
    verifications = db.relationship('VerificationResult', backref='user', lazy='dynamic')
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserHistory(db.Model):
    __tablename__ = 'user_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # e.g., 'article_verified', 'profile_updated'
    action_details = db.Column(db.Text, nullable=True)  # JSON or description of the action
    article_url = db.Column(db.String(500), nullable=True)  # URL of the article if applicable
    article_title = db.Column(db.String(200), nullable=True)  # Title of the article if applicable
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserHistory {self.action_type} by User {self.user_id}>'


class SavedArticle(db.Model):
    __tablename__ = 'saved_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_url = db.Column(db.String(500), nullable=False)
    article_title = db.Column(db.String(200), nullable=False)
    article_content = db.Column(db.Text, nullable=True)
    article_source = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SavedArticle {self.article_title[:30]}... by User {self.user_id}>'


class VerificationResult(db.Model):
    __tablename__ = 'verification_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Can be null for anonymous verifications
    original_text = db.Column(db.Text, nullable=False)
    authenticity_score = db.Column(db.Integer, nullable=False)  # 0-100 score
    key_findings = db.Column(db.Text, nullable=True)  # Stored as JSON
    differences = db.Column(db.Text, nullable=True)  # Stored as JSON
    supporting_evidence = db.Column(db.Text, nullable=True)  # Stored as JSON
    score_breakdown = db.Column(db.Text, nullable=True)  # Stored as JSON
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Helper methods for JSON fields
    def set_key_findings(self, findings_list):
        self.key_findings = json.dumps(findings_list)
        
    def get_key_findings(self):
        return json.loads(self.key_findings) if self.key_findings else []
    
    def set_differences(self, differences_list):
        self.differences = json.dumps(differences_list)
        
    def get_differences(self):
        return json.loads(self.differences) if self.differences else []
    
    def set_supporting_evidence(self, evidence_list):
        self.supporting_evidence = json.dumps(evidence_list)
        
    def get_supporting_evidence(self):
        return json.loads(self.supporting_evidence) if self.supporting_evidence else []
    
    def set_score_breakdown(self, breakdown_dict):
        self.score_breakdown = json.dumps(breakdown_dict)
        
    def get_score_breakdown(self):
        return json.loads(self.score_breakdown) if self.score_breakdown else {}
    
    def __repr__(self):
        return f'<VerificationResult id={self.id} score={self.authenticity_score}>'


class SearchQuery(db.Model):
    __tablename__ = 'search_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Can be null for anonymous searches
    query_text = db.Column(db.Text, nullable=False)
    headlines = db.Column(db.Text, nullable=True)  # Stored as JSON
    search_results = db.Column(db.Text, nullable=True)  # Stored as JSON (URLs)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_headlines(self, headlines_list):
        self.headlines = json.dumps(headlines_list)
        
    def get_headlines(self):
        return json.loads(self.headlines) if self.headlines else []
    
    def set_search_results(self, results_dict):
        self.search_results = json.dumps(results_dict)
        
    def get_search_results(self):
        return json.loads(self.search_results) if self.search_results else {}
    
    def __repr__(self):
        return f'<SearchQuery id={self.id} query="{self.query_text[:30]}...">'


