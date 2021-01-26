import time

import click
from werkzeug.security import gen_salt

from main import app
from models import db, Client


@click.command()
@click.option('--name', required=True, help="Client name")
@click.option('--redirect_uri', required=True, multiple=True, help="Redirect uri (may be used multiple times)")
def register_client(name, redirect_uri):
    """
    Register a new OIDC client.

    Example:
    python register_client.py
      --name my-new-app
      --redirect_uri https://app.com/logincallback
      --redirect_uri https://localhost/logincallback

    Currently only allows confidential clients (basic auth)
    for use in auth code grant flow.
    """

    client_id = gen_salt(24)
    client_secret = gen_salt(48)

    new_client = Client(
            client_id=client_id,
            client_secret=client_secret,
            client_id_issued_at=int(time.time()),
    )
    new_client_metadata = {
            "client_name": name,
            "grant_types": "authorization_code",
            "redirect_uris": redirect_uri,
            "response_types": "code",
            "scope": "openid user",
            "token_endpoint_auth_method": "client_secret_basic",
    }
    new_client.set_client_metadata(new_client_metadata)

    with app.app_context():
        db.session.add(new_client)
        db.session.commit()

    click.echo("  Client Name: " + name)
    click.echo("Redirect URIs: " + str(redirect_uri))
    click.echo("    client_id: " + client_id)
    click.echo("client_secret: " + client_secret)

    return client_id, client_secret

if __name__ == '__main__':
    register_client()
