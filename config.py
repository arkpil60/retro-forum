import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ForumSecretKey_123')
    
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_NAME = "forum_db"
    DB_USER = "postgres"
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'ParolOtPostgre_123')

    MAINTENANCE_MODE = True