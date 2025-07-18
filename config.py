class Config:
    SECRET_KEY = 'dev'  # Change this in production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///weekly_report.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
