# SQLite and in-memory for now...
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

PRIVATE_KEY_PATH = '/var/www/wsgi/privatekey.pem'


DEBUG = False

# Disabled by default; setting here to silence warning
SQLALCHEMY_TRACK_MODIFICATIONS = False
