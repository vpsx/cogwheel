# SQLite and in-memory for now...
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

PRIVATE_KEY_PATH = '/etc/cixiri/rsa/privatekey.pem'


DEBUG = False

# OIDC server metadata for .well-known/oauth-authorization-server
OAUTH2_METADATA_FILE = '/etc/cixiri/oauth2_metadata.json'

# Disabled by default; setting here to silence warning
SQLALCHEMY_TRACK_MODIFICATIONS = False
