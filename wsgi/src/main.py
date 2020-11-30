# Docs on how Shibboleth info is passed from server to application:
# https://wiki.shibboleth.net/confluence/display/SP3/ApplicationIntegration
# https://wiki.shibboleth.net/confluence/display/SP3/AttributeAccess#AttributeAccess-REMOTE_USER

from flask import Flask, request
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World! I\'m a Flask app!'


@app.route('/apache')
def apache():
    # Inspect request context
    print("request:")
    print(request)
    print(dir(request))
    print(request.remote_user)
    return "REMOTE_USER is..... " + request.remote_user


@app.route('/breakpoint')
def breakpoint():
    import pdb; pdb.set_trace()
    return "Debugger weeee"


from flask_sqlalchemy import SQLAlchemy
# SQLite and in-memory for now...
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # other columns

    # TODO:
    # Example REMOTE_USER from mod_shib:
    # urn:mace:incommon:uchicago.edu!https://zlc.planx-pla.net/sp!ABCdef123456SAMLuseridstring=
    # Need to think about what columns to put in this table.
    # It will depend, probably, on what I need to put in the id_token ultimately.
    # For now, let's just stick the entire REMOTE_USER string into one column.
    # By the way, how do we get user attributes from the SAML assertion from here (here = the WSGI app)?
    # You will need those in order to get e.g. a sensible value for username.
    shib_id = db.Column(db.String)

    def get_user_id(self):
        return self.id

from authlib.integrations.sqla_oauth2 import OAuth2ClientMixin

class Client(db.Model, OAuth2ClientMixin):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = db.relationship('User')


from authlib.integrations.sqla_oauth2 import OAuth2TokenMixin

class Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = db.relationship('User')


from authlib.integrations.sqla_oauth2 import OAuth2AuthorizationCodeMixin

class AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'authorization_codes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = db.relationship('User')


# Make dem tables
db.create_all()


# Fake-register a test client...
test_client = Client(client_id='test_client')
test_client_metadata = {
        "client_name": "test_client_name",
        "client_uri": "test_client_uri",
        #"grant_types": blah,
        "redirect_uris": "test_client_redirect_uri",
        "response_types": "code",
        #, scope, token_endpoint_auth_method...
}
test_client.set_client_metadata(test_client_metadata)
db.session.add(test_client)
db.session.commit()
# Done registering test client.


from authlib.oauth2.rfc6749 import grants

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def save_authorization_code(self, code, request):
        client = request.client
        auth_code = AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=request.user.id,
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
server.register_grant(AuthorizationCodeGrant)


from flask import request, render_template
#from your_project.auth import current_user

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
    return server.create_token_response()
