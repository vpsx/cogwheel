# Cixiri

SAML SP and OIDC IdP on Apache.

The implementation extends the InCommon TIER Shibboleth SP docker base image,
found [here](https://github.internet2.edu/docker/shib-sp/tree/3.1.0_04172020).

-----------------------------------------------------------------------

## Reference

Build: `docker build -t cixiri .`
Run: `docker run --name cixiri -p 1233:80 -p 1234:443 cixiri`

(Note: You can't build or run this before you have completed setup/config,
the steps for which are detailed below.)

-----------------------------------------------------------------------

## Prerequisites

If you are going to use this for InCommon integration you will first need
to register an InCommon Service Provider that you will use.

- [InCommon Federation Manager](https://spaces.at.internet2.edu/display/federation/Federation+Manager)
- [InCommon docs: Add a service provider](https://spaces.at.internet2.edu/display/federation/federation-manager-add-sp)

Signing and encryption certificates and keys
should be generated according to [these instructions](https://spaces.at.internet2.edu/display/federation/Key+Generation).
You can use the same set for both signing and encryption.
Save these in the top level directory with the following names:
`sp-encrypt-cert.pem`, `sp-encrypt-key.pem`, `sp-signing-cert.pem`,
`sp-signing-key.pem`.

If you are setting up something other than InCommon, still save the SP's
signing and encryption keys/certs with those names.

-----------------------------------------------------------------------

## Setup and configuration

As described above, make sure you have saved your SP's signing/encryption certs
and keys with the correct names in the top level directory.

Then, IF your SP is an InCommon SP and you want to use the InCommon Metadata
Service (if you don't know, assume that the answer is yes):

- Download the InCommon medatada signing certificate and save it as mdqsigner.pem:
  `curl https://md.incommon.org/certs/inc-md-cert-mdq.pem > mdqsigner.pem`
- Check the fingerprints:
  `cat mdqsigner.pem | openssl x509 -sha1 -noout -fingerprint`
  `cat mdqsigner.pem | openssl x509 -sha256 -noout -fingerprint`
  The results should match the fingerprints listed [here](https://spaces.at.internet2.edu/display/MDQ/production+metadata+signing+key).

        (Note for March 2021: The signing certificate url above [may change](https://spaces.at.internet2.edu/display/MDQ/migrate-to-mdq).
        The doc above says to migrate to use the "new" md endpoints, which
        it links, but the linked docs still list "md.incommon.org"... which is
        supposed to be the legacy service. Anyway, check back in March 2021.)

Then, make a copy of `template.ssl.conf` and save it as `ssl.conf`; edit it
according to the instructions in its header comment.

Make a copy of `template.shibboleth2.xml` and save it as `shibboleth2.xml`;
edit it according to the instructions in its header comment.

-----------------------------------------------------------------------
