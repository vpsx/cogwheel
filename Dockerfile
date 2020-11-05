# https://github.internet2.edu/docker/shib-sp/tree/3.1.0_04172020
# Based on CentOS 7
FROM tier/shibboleth_sp:3.1.0_04172020

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
