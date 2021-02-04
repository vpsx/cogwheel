# Docs on how Shibboleth info is passed from server to application:
# https://wiki.shibboleth.net/confluence/display/SP3/ApplicationIntegration
# https://wiki.shibboleth.net/confluence/display/SP3/AttributeAccess#AttributeAccess-REMOTE_USER

from flask import Flask, request
from models import db, AuthorizationCode, Client, Token, User

app = Flask(__name__)

# Load configuration--default, then custom. Path to latter set in Dockerfile.
app.config.from_object('default_settings')
app.config.from_envvar('PATH_TO_APP_CONFIG')

# Configure app to work with SQLAlchemy
db.init_app(app)
# Create tables.
# SQLAlchemy object not bound to app, so pass in app as arg.
# Alternatively could push an app context.
db.create_all(app=app)


from authlib.oauth2.rfc6749 import grants

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):

    def save_authorization_code(self, code, request):
        # openid request MAY have "nonce" parameter
        nonce = request.data.get('nonce')
        client = request.client
        auth_code = AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=request.user.id,
            nonce=nonce,
        )
        db.session.add(auth_code)
        db.session.commit()
        return auth_code

    def query_authorization_code(self, code, client):
        item = AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id).first()
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        db.session.delete(authorization_code)
        db.session.commit()

    def authenticate_user(self, authorization_code):
        return User.query.get(authorization_code.user_id)



from authlib.oidc.core import grants, UserInfo

class OpenIDCode(grants.OpenIDCode):
    def exists_nonce(self, nonce, request):
        exists = AuthorizationCode.query.filter_by(
            client_id=request.client_id, nonce=nonce
        ).first()
        return bool(exists)

    def get_jwt_config(self, grant):
        """Get the JWT configuration for OpenIDCode extension. The JWT
        configuration will be used to generate ``id_token``.
        """
        # Get iss/hostname from WSGI environment, i.e. from Apache VirtualHost config,
        # to eliminate the need to manually configure the WSGI app with a hostname and
        # then manually ensure that both config values match
        iss = request.environ['SERVER_NAME']

        # Read in private signing key
        with open(app.config["PRIVATE_KEY_PATH"]) as f:
            private_key = f.read()

        return {
            'key': private_key,
            'alg': 'RS256',
            'iss': iss,
            'exp': 3600,
        }

    def generate_user_info(self, user, scope):
        # The "sub" claim should either be unique issuer-wide or
        # globally unique, and it should be a StringOrURI.
        # Technically a stringified user.id would be issuer-unique,
        # but I think it is more sensible to just use user.shib_id.
        # Will still also publish "shib_id" field.

        user_info = UserInfo(sub=user.shib_id, shib_id=user.shib_id)

        # Add this when can get the "mail" SAML Attribute!
        #if 'email' in scope:
        #    user_info['email'] = user.email

        return user_info



from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func
)
query_client = create_query_client_func(db.session, Client)
save_token = create_save_token_func(db.session, Token)

server = AuthorizationServer(
    app, query_client=query_client, save_token=save_token
)

# register AuthorizationCodeGrant to grant endpoint
server.register_grant(AuthorizationCodeGrant, [OpenIDCode(require_nonce=False)])


from flask import request, render_template

def get_or_create_shib_user():
    if request.remote_user:
        user = User.query.filter(User.shib_id == request.remote_user).one_or_none()
        if not user:
            print("User not found in db; creating...")
            new_user = User(shib_id=request.remote_user)
            db.session.add(new_user)
            db.session.commit()
            print("User created.")
            user = new_user
        return user
    return "No value for request.remote_user--is this being called outside a request context?"


@app.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    # Login is required since we need to know the current resource owner.
    # It can be done with a redirection to the login page, or a login
    # form on this authorization page.

    current_user = get_or_create_shib_user()

    if request.method == 'GET':
        grant = server.validate_consent_request(end_user=current_user)
        return render_template(
            'authorize.html',
            grant=grant,
            user=current_user,
        )
    confirmed = request.form['confirm']
    if confirmed:
        # granted by resource owner
        return server.create_authorization_response(grant_user=current_user)
    # denied by resource owner
    return server.create_authorization_response(grant_user=None)


@app.route('/oauth/token', methods=['POST'])
def issue_token():
    """
    The client should make the request with a Basic auth header and
    Content-Type: application/x-www-form-urlencoded
    """
    return server.create_token_response()

@app.route('/.well-known/oauth-authorization-server')
def well_known():
    return server.metadata


from authlib.jose import JsonWebKey, KeySet

@app.route('/jwks.json')
def jwks():
    with open(app.config["PUBLIC_KEY_PATH"]) as f:
        public_key_data = f.read()
    public_key = JsonWebKey.import_key(public_key_data, {"kty": "RSA"})
    keyset = KeySet([public_key])
    return keyset.as_json()
