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
