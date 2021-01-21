build () {
    docker build -t cogwheel .
}
run () {
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
}
cycle () {
    docker kill cogwheel
    docker rm cogwheel
    docker build -t cogwheel .
    run
}
logs () {
    docker logs cogwheel
}
shell () {
    docker exec -it cogwheel bash
}
poke () {
    docker exec -w /var/www/wsgi/wsgi-scripts cogwheel touch app.wsgi
}
