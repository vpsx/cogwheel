# https://github.internet2.edu/docker/shib-sp/tree/3.1.0_04172020
# Based on CentOS 7
FROM tier/shibboleth_sp:3.1.0_04172020

## Provide SSL certificate and key
COPY ssl_cert.pem /etc/pki/tls/certs/localhost.crt
COPY ssl_key.pem /etc/pki/tls/private/localhost.key

# Provide the SP's private keys and certificates.
# Must match the keys and certs of the SP registered with InCommon.
# May use the same key/cert pair for signing and encryption.
COPY sp-encrypt-cert.pem /etc/shibboleth/sp-encrypt-cert.pem
COPY sp-encrypt-key.pem  /etc/shibboleth/sp-encrypt-key.pem
COPY sp-signing-cert.pem /etc/shibboleth/sp-signing-cert.pem
COPY sp-signing-key.pem  /etc/shibboleth/sp-signing-key.pem

# Provide the InCommon metadata signing certificate.
# See comments in template.shibboleth2.xml for instructions.
COPY mdqsigner.pem /etc/shibboleth/mdqsigner.pem

# Provide shibboleth configuration.
COPY shibboleth2.xml /etc/shibboleth/shibboleth2.xml

# Provide SSL configuration.
COPY ssl.conf /etc/httpd/conf.d/ssl.conf



# ---------------------------------------------------------------

RUN yum install --assumeyes \
    # Apache development package is required for compiling third party Apache modules
    # (mod_wsgi being the one of interest to us)
    httpd-devel \
    # Python and Python dev package are required for installing mod_wsgi, along with gcc
    python3 python3-devel gcc


# mod_wsgi is installed via pip and then manually connected to the existing Apache install.
# Note: The pip method of installing mod_wsgi is recommended by the mod_wsgi maintainer.
# One of the main advantages of this method is that it provides the mod_wsgi-express tool
# for automated configuration and management of the Apache server.
# However, since the Shibboleth SP base image already provides and runs an Apache installation,
# we are NOT using mod_wsgi-express (nor installing mod_wsgi-standalone).
# Nevertheless the pip3 method is still simpler than the CMMI method.
# More info: https://pypi.org/project/mod-wsgi/
RUN pip3 install mod_wsgi

# ...except this one and only time where we do use mod_wsgi-express, to copy mod_wsgi into
# the existing Apache installation.  See "Connecting into Apache installation", also at
# https://pypi.org/project/mod-wsgi/
RUN mod_wsgi-express install-module

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -

# Copy the wsgi app, which contains all the OIDC code
COPY ./wsgi /var/www/wsgi


# Append additional config to main Apache config file.
# This seemed like the simplest and dumbest method; therefore, do switch to `Include`
# directives if it becomes sensible to do so.
COPY append_httpd.conf /tmp/append_httpd.conf
RUN cat /tmp/append_httpd.conf >> /etc/httpd/conf/httpd.conf && rm /tmp/append_httpd.conf

# Append additional config to supervisord config file.
COPY append_supervisord.conf /tmp/append_supervisord.conf
RUN cat /tmp/append_supervisord.conf >> /etc/supervisor/supervisord.conf && rm /tmp/append_supervisord.conf


# Set up WSGI application config and OAuth2 server metadata
RUN mkdir /etc/cixiri
COPY wsgi_settings.py /etc/cixiri/wsgi_settings.py
ENV PATH_TO_APP_CONFIG=/etc/cixiri/wsgi_settings.py
COPY oauth2_metadata.json /etc/cixiri/oauth2_metadata.json

WORKDIR /var/www/wsgi
RUN . $HOME/.poetry/env \
    # Create virtualenv in /var/www/wsgi/.venv
    # It's not important where the venv is; this just makes it explicit and obvious.
    # If you change this, you should change python-home in the WSGIDaemonProcess directive
    # of the WSGI virtualhost def.
    && poetry config virtualenvs.in-project true \
    # Change this to just "poetry install" if you want to use dev dependencies
    && poetry install --no-dev


# Just for convenience when knocking around inside container
ENV PKGS=/var/www/wsgi/.venv/lib/python3.6/site-packages/
