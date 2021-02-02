from authlib.integrations.sqla_oauth2 import (
        OAuth2AuthorizationCodeMixin,
        OAuth2ClientMixin,
        OAuth2TokenMixin,
)
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # OTHER COLUMNS:
    # At the moment UChicago IdP is not returning the SAML Attributes
    # that my SP is requesting (mail, eduPersonPrincipalName, ...)
    # and I have no other InCommon credentials (for another IdP) to test with. :(
    # In future perhaps add more columns here for different SAML Attributes.

    # This will be the persistent-id which mod_shib puts into REMOTE_USER. Example:
    # urn:mace:incommon:uchicago.edu!https://zlc.planx-pla.net/sp!ABCdef123456SAMLuseridstring=
    shib_id = db.Column(db.String)

    def get_user_id(self):
        return self.id


class Client(db.Model, OAuth2ClientMixin):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = db.relationship('User')


class Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = db.relationship('User')


class AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'authorization_codes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = db.relationship('User')
