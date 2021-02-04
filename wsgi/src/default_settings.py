# This should be overridden in wsgi_settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

PRIVATE_KEY_PATH = '/etc/cogwheel/rsa/privatekey.pem'
PUBLIC_KEY_PATH = '/etc/cogwheel/rsa/publickey.pem'


DEBUG = False

# OIDC server metadata for .well-known/oauth-authorization-server
OAUTH2_METADATA_FILE = '/etc/cogwheel/oauth2_metadata.json'

# Disabled by default; setting it explicitly here to silence warning
SQLALCHEMY_TRACK_MODIFICATIONS = False
