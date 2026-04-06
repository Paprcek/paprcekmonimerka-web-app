import os
import datetime

class Config:
    # Tajné klíče a API
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default_fallback_secret_key")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    SENTRY_DSN = os.getenv('SENTRY_DSN')

    # Nastavení Mailu
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'paprcekmonimerka@gmail.com'
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = 'paprcekmonimerka@gmail.com'

    # Ostatní nastavení
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)