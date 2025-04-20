from app import app, db
from models import User, UserHistory, SearchQuery, SavedArticle, VerificationResult
from flask import flash

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
    
    # This message will be displayed to the user when they next visit the application
    # It will be stored in the session and displayed in the templates
    # The message will be visible in the dashboard and profile pages
    print("\nDatabase initialization complete!")
    print("The following tables were created:")
    print("- Users: Store user accounts and authentication information")
    print("- UserHistory: Track user actions and activity")
    print("- SearchQueries: Store search history and results")
    print("- SavedArticles: Save articles for later reference")
    print("- VerificationResults: Store content verification results and scores")
    print("\nYou can now view this data in your user dashboard!")
    print("Access your dashboard by logging in and clicking on 'Dashboard' in the user menu.")

