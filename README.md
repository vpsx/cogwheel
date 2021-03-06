# Cogwheel

SAML SP and OIDC IdP implemented with Apache httpd, Shibboleth SP3, and
Authlib. Authenticate with a SAML IdP or federation using OIDC.

The implementation extends the InCommon TIER Shibboleth SP docker base image,
found [here](https://github.internet2.edu/docker/shib-sp/tree/3.1.0_04172020).

-----------------------------------------------------------------------

## Reference

Build:
```
docker build -t cogwheel .
```
Run:
```
docker run \
--name cogwheel \
--publish 1233:80 --publish 1234:443 \
--mount type=bind,source="$(pwd)"/ssl_cert.pem,target=/etc/pki/tls/certs/localhost.crt \
--mount type=bind,source="$(pwd)"/ssl_key.pem,target=/etc/pki/tls/private/localhost.key \
--mount type=bind,source="$(pwd)"/sp-encrypt-cert.pem,target=/etc/shibboleth/sp-encrypt-cert.pem \
--mount type=bind,source="$(pwd)"/sp-encrypt-key.pem,target=/etc/shibboleth/sp-encrypt-key.pem \
--mount type=bind,source="$(pwd)"/sp-signing-cert.pem,target=/etc/shibboleth/sp-signing-cert.pem \
--mount type=bind,source="$(pwd)"/sp-signing-key.pem,target=/etc/shibboleth/sp-signing-key.pem \
--mount type=bind,source="$(pwd)"/mdqsigner.pem,target=/etc/shibboleth/mdqsigner.pem \
--mount type=bind,source="$(pwd)"/shibboleth2.xml,target=/etc/shibboleth/shibboleth2.xml \
--mount type=bind,source="$(pwd)"/ssl.conf,target=/etc/httpd/conf.d/ssl.conf \
--mount type=bind,source="$(pwd)"/wsgi_settings.py,target=/etc/cogwheel/wsgi_settings.py \
--mount type=bind,source="$(pwd)"/oauth2_metadata.json,target=/etc/cogwheel/oauth2_metadata.json \
--mount type=bind,source="$(pwd)"/rsa_privatekey.pem,target=/etc/cogwheel/rsa/privatekey.pem \
--mount type=bind,source="$(pwd)"/rsa_publickey.pem,target=/etc/cogwheel/rsa/publickey.pem \
cogwheel
```

The Dockerfile contains a comment very briefly describing each mounted file;
otherwise see below for details on each file.

(Note: You can't build or run this before you have completed setup/config,
the steps for which are detailed below.)

-----------------------------------------------------------------------

## Prerequisites

#### Register an InCommon Service Provider

If you are going to use this for InCommon integration you will first need
to register an InCommon Service Provider that you will use.

- [InCommon Federation Manager](https://spaces.at.internet2.edu/display/federation/Federation+Manager)
- [InCommon docs: Add a service provider](https://spaces.at.internet2.edu/display/federation/federation-manager-add-sp)

The SP registration form will require that you provide
signing and encryption certificates and keys for the SP.
These should be generated according to [these instructions](https://spaces.at.internet2.edu/display/federation/Key+Generation).
You can use the same set for both signing and encryption.
Save the certs and keys in the top level directory with the following names:
`sp-encrypt-cert.pem`, `sp-encrypt-key.pem`, `sp-signing-cert.pem`,
`sp-signing-key.pem`.

If you are setting up something other than InCommon, still save the SP's
signing and encryption keys/certs with those names.

#### Obtain a TLS/SSL certificate for your domain name

Save the cert and key in the top level directory with the names `ssl_cert.pem`
and `ssl_key.pem`.

To make a self-signed certificate for testing:
`openssl req -x509 -newkey rsa -nodes -out ssl_cert.pem -keyout ssl_key.pem`

-----------------------------------------------------------------------

## Setup and configuration

As described above, make sure you have saved your SP's signing/encryption certs
and keys with the correct names in the top level directory.

#### To use InCommon MDS: Download md signing cert

Then, IF your SP is an InCommon SP and you want to use the InCommon Metadata
Service (if you don't know, assume that the answer is yes):

- Download the InCommon metadata signing certificate and save it as mdqsigner.pem:
  `curl https://md.incommon.org/certs/inc-md-cert-mdq.pem > mdqsigner.pem`
- Check the fingerprints:
  `cat mdqsigner.pem | openssl x509 -sha1 -noout -fingerprint`
  `cat mdqsigner.pem | openssl x509 -sha256 -noout -fingerprint`
  The results should match the fingerprints listed [here](https://spaces.at.internet2.edu/display/MDQ/production+metadata+signing+key).

        (Note for March 2021: The signing certificate url above [may change](https://spaces.at.internet2.edu/display/MDQ/migrate-to-mdq).
        The doc above says to migrate to use the "new" md endpoints, which
        it links, but the linked docs still list "md.incommon.org"... which is
        supposed to be the legacy service. Anyway, check back in March 2021.)


#### Configure httpd VirtualHost

Then, make a copy of `template.ssl.conf` and save it as `ssl.conf`; edit it
according to the instructions in its header comment. (At the moment this merely
entails supplying a ServerName.)

#### Configure Shibboleth

Make a copy of `template.shibboleth2.xml` and save it as `shibboleth2.xml`;
edit it according to the instructions in its header comment. (At the moment
this merely entails supplying your SP's EntityID, unless you want to customise
the Shibboleth behavior.)

#### Configure WSGI/Flask app

You need to supply a database as well as an RSA keypair.

To point to your database:
1. Open `wsgi_settings.py` and edit the value for `SQLALCHEMY_DATABASE_URI`.

To generate an RSA keypair:

1. Generate private key:
   `openssl genpkey -algorithm RSA256 -out rsa_privatekey.pem -outform pem`
1. Then generate public key:
   `openssl pkey -in wsgi/privatekey.pem -inform pem -out rsa_publickey.pem -outform pem -pubout`


Background info on Flask configuration: The Flask app configuration can be
edited via `wsgi_settings.py` in the top level directory; this will be mounted
to `/etc/cogwheel/wsgi_settings.py` in the Docker image. The app will first read in
default configuration from `wsgi/src/default_settings.py` and then override
this with config from `wsgi_settings.py`.

#### OAuth2/OIDC Server Metadata

Make a copy of `template.oauth2_metadata.json` and name it
`oauth2_metadata.json`. Edit the hostnames in the URLs (they should match the
ServerName entered earlier in `httpd.conf`). The contents of this file
constitute the OIDC server metadata per RFC 8414 and will be served at
`/.well-known/oauth-authorization-server`. For more information and a list of
metadata values see [here](https://tools.ietf.org/html/rfc8414#section-2).


-----------------------------------------------------------------------

## Interactive debugging

You can set up the server such as to enable the use of pdb, but it is a rather
involved process. See [here](https://modwsgi.readthedocs.io/en/develop/user-guides/debugging-techniques.html#python-interactive-debugger) for background information on the steps below.

1. In your `ssl.conf` in the VirtualHost definition, comment out both the
   WSGIDaemonProcess directive and the WSGIProcessGroup directive.
1. In `append_httpd.conf` uncomment the section "FOR ENABLING INTERACTIVE
   DEBUGGER".
1. In `append_supervisord.conf` uncomment the section "FOR ENABLING INTERACTIVE
   DEBUGGER". If you like you can also uncomment the section "FOR ENABLING
   SUPERVISORCTL", but this is not essential.


Now you can edit the Python code and add your breakpoints. Rebuild and restart
your container. Then before doing anything else, start up a shell in the
container and:
1. Kill the server, `httpd -k stop`
1. Restart the server, `httpd -X`
This is just so that now you have a way to write to stdin.

And now you can hit your breakpoints and start debugging.

OPTIONAL:
1. To use the optional dev dependencies, change `poetry install
   --no-dev` in the Dockerfile to just `poetry install`.
1. To drop into the debugger on every request, uncomment the section "FOR
   ENTHUSIASTIC INTERACTIVE DEBUGGER" in `wsgi/wsgi-scripts/app.wsgi`.

-----------------------------------------------------------------------
