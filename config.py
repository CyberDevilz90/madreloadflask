class Config:
    DB_USER = "postgres"
    DB_PASS = "admin"
    DB_NAME = "madreload-api"
    DB_HOST = "localhost"
    DB_PORT = "5432"

    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False