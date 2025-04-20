class Config:
    # Flask-Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'salunkhesantosh787@gmail.com'
    MAIL_PASSWORD = 'ohjq iqcn zrpt xpco'

    # Google Custom Search API configuration
    GOOGLE_API_KEY = "AIzaSyB2nlYuSgnoKLBKC4aF2nfF2drE3ZWIMNk"
    GOOGLE_CSE_ID = "15c198a8769a045ec"
    
    # Flask configuration
    SECRET_KEY = 'your-secret-key-goes-here'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin@localhost/newsguard'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    
