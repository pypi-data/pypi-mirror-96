..  Note to the editor: beware of implicit inline
    targets aliasing, keep global title different from all commands

=============================================================================
caucase - Certificate Authority for Users, Certificate Authority for SErvices
=============================================================================

Overview
========

The goal of caucase is to automate certificate issuance and renewal without
constraining how the certificate will be used.

For example, there is no assumption that the certificate will be used to
secure HTTP, nor to serve anything at all: you may need certificates to
authenticate users, or sign your mails, or secure an SQL server socket.

As an unfortunate consequence, it is not possible for caucase to automatically
validate a signing request content against a service (ex: as one could check
the certificate for an HTTPS service was requested by someone with the ability
to make it serve a special file).

This also means that, while caucase imposes RFC-recommended constraints on many
certificate fields and extensions to be worthy of trust, it imposes no
constraint at all on subject and alternate subject certificate fields.

To still allow certificates to be used, caucase uses itself to authenticate
users (humans or otherwise) who implement the validation procedure: they tell
caucase what certificates to emit. Once done, any certificate can be
prolonged at a simple request of the key holder while the to-renew
certificate is still valid (not expired, not revoked).

Bootstrapping the system (creating the first service certificate for
`caucased`_ to operate on HTTPS, and creating the first user certificate to
control further certificate issuance) works by caucase automatically signing a
set number of certificates upon submission.

Vocabulary
==========

Caucase manipulates the following asymmetric cryptography concepts.

- Key pair: A private key and corresponding public key. The public key can be
  derived from the private key, but not the other way around. As a consequence,
  the private key is itself considered to be a key pair.

- Certificate: A certificate is the assurante, by a certificate authority,
  that a given public key and set of attributes belong to an authorised entity.
  Abbreviated cert or crt. A certificate is by definition signed by a CA.

- Certificate Authority: An entry, arbitrarily trusted (but worthy of trust by
  its actions and decision) which can issue certificates. Abbreviated CA.

- Certificate signing request: A document produced by an entity desiring to get
  certified, which they send to a certificate authority. The certificate signing
  request contains the public key and desired set of attributes that the CA
  should pronounce itself on. The CA has all liberty to issue a different set
  of attributes, or to not issue a certificate.

- Certificate revocation list: Lists the certificates which were issued by a CA
  but which should not be trusted anymore. This can happen for a variety of
  reasons: the private key was compromised, or its owning entity should not be
  trusted anymore (ex: entity's permission to access to protected service was
  revoked).

- PEM: A serialisation mechanism commonly used for various cryptographic data
  pieces. It relies on base64 so it is 7-bits-safe (unlike DER), and is very
  commonly supported. Caucase exclusively uses PEM format.

Validity period
===============

Cryptographic keys wear out as are used and as they age.

Of course, they do not bit-rot nor become thinner with use. But each time one
uses a key and each minute an attacker had access to a public key, fractions
of the private key bits are inevitably leaked, weakening it overall.

So keys must be renewed periodically to preserve intended security level. So
there is a limited life span to each certificate, including the ones emitted by
caucase.

The unit duration for caucase-emitted certificates is the "normal" certificate
life span. It default to 93 days from the moment the certificate was signed,
or about 3 months.

Then the CA certificate has a default life span of 4 "normal" certificate
validity periods. As CA renewal happens in caucase without x509-level cross
signing (by decision, to avoid relying on intermediate CA support on
certificate presenter side and instead rely on more widespread
multi-CA-certificate support on verifier side), there is a hard lower bound of
3 validity periods, under which the CA certificate cannot be reliably renewed
without risking certificate validation issues for emitted "normal"
certificates. CA certificate renewal is composed of 2 phases:

- Passive distribution phase: current CA certificate has a remaining life span
  of less than 2 "normal" certificate life spans: a new CA certificate is
  generated and distributed on-demand (on "normal" certificate renewal and
  issuance, on CRL retrieval with caucase tools...), but not used to sign
  anything.
- Active use phase: new CA certificate is valid for more than one "normal"
  certificate life span. This means that all existing certificates which are
  still in active use had to be renewed at least once since the new CA
  certificate exists. This means all the certificate holders had the
  opportunity to learn about the new CA certificate. So the new CA certificate
  starts being used to sign new certificates, and the old CA certificate falls
  out of use as its signed "normal" certificates expire.

By default, all caucase tools will generate a new private key unrelated to the
previous one on each certificate renewal.

Lastly, there is another limited validity period, although not for the same
reasons: the list of revoked certificates also has a maximum life span. In
caucase, the CRL is re-generated whenever it is requested and:

- there is no previous CRL
- previous CRL expired
- any revocation happened since previous CRL was created

Here is an illustration of the certificate and CA certificate renewal process::

  Time from first caucased start:
    +--------+--------+--------+--------+--------+--------+--------+-->
  Certificate 1 validity:      |                 |                 |
    |[cert 1v1]  [cert 1v3]  [cert 1v5]  [cert 1v7]  [cert 1v9]  [ce...
    |      [cert 1v2]  [cert 1v4]  [cert 1v6]  [cert 1v8]  [cert 1vA]
  Certificate 2 validity:      |                 |                 |
    |    [cert 2v1]  [cert 2v3]| [cert 2v5]  [cert 2v7]  [cert 2v9]|
    |          [cert 2v2]  [cert 2v4]  [cert 2v6]| [cert 2v8]  [cert...
  CA certificates validity:    |                 |                 |
    [ca v1                     |        ]        |                 |
    |                 [ca v2   |                 |        ]        |
    |                          |        [ca v3   |                 |...
    |                          |                 |        [ca v4   |...
  CRL validity for CA1:        |                 |                 |
    [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][  ]        |                 |
  CRL validity for CA2:        |                 |                 |
    |                 [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][  ]        |
  CRL validity for CA3:        |                 |                 |
    |                          |        [ ][ ][ ][ ][ ][ ][ ][ ][ ][...
  CA renewal phase:            |                 |                 |
    |none             |passive |active  |passive |active  |passive |...
  Active CA:                   |                 |                 |
    [ca v1                    ][ca v2           ][ca v3            |...
  Trust anchor:                |                 |                 |
    [ca v1                     |       ][ca v2   |       ][ca v3   |...

Legend::

  +--------+ : One certificate validity period (default: 93 days)

Points of interest:

- this illustration assumes no revocation happen
- there usually are 2 simultaneously-valid CA certificates
- there usually are 2 simultaneously-valid CRLs overall, one per CA certificate
- the first ``cert 1`` signed by CA v2 is ``cert 1v6``
- the first ``cert 2`` signed by CA v2 is ``cert 1v5``

Commands
========

Caucase provides several commands to work with certificates.

caucase
+++++++

Reference caucase "one-shot" client.

This command is intended to be used for isolated actions:

- listing and signing pending certificate signature requests

- revoking certificates

It is also able to submit certificate signing requests, retrieve signed
certificates, requesting certificate renewals and updating both
CA certificates and revocation lists, but you may be interested in using
`caucase-updater`_ for this instead.

caucase-updater
+++++++++++++++

Reference caucase certificate renewal daemon.

Monitors a key pair, corresponding CA certificate and CRL, and renew them
before expiration.

When the key-pair lacks a signed certificate, issues a pre-existing CSR to
caucase server and waits for the certificate to be issued.

caucase-probe
+++++++++++++

Caucase server availability tester.

Performs minimal checks to verify a caucase server is available at given URL.

caucase-rerequest
+++++++++++++++++

Utility allowing to re-issue a CSR using a locally-generated private key.

Intended to be used in conjunction with `caucase-updater`_ when user cannot
generate the CSR on the system where the certificate is desired (ex: automated
HTTPS server deployment), where user is not the intended audience for
caucase-produced certificate:

- User generates a CSR on their own system, and signs it with any key (it will
  not be needed later
- User sends the CSR to the system where the certificate is desired
- User gets caucase-rerequest to run on this CSR, producing a new private key
  and a CSR similar to issued one, but signed with this new private key
- From then on, caucase-updater can take over

This way, no private key left their original system, and user could still
freely customise certificate extensions.

caucase-key-id
++++++++++++++

Utility displaying the identifier of given key, or the identifier of keys
involved in given backup file.

Allows identifying users which hold a private key candidate for restoring a
caucased backup (see `Restoration procedure`_).

caucased
++++++++

Reference caucase server daemon.

This daemon provides access to both CAU and CAS services over both HTTP and
HTTPS.

It handles its own certificate issuance and renewal, so there is no need to use
`caucase-updater`_ for this service.

CORS
----

caucased implements CORS protection: when receiving a cross-origin request,
it will respond with 401 Unauthorized, with the WWW-Authenticate header set to
a custom scheme ("cors") with an "url" parameter containing an URI template
with one variable field: "return" (more on it later).

Upon receiving this response, the application is expected to render the URL
template and redirect the user to resulting URL. There, the user will be
informed of the cross-origin access attempt, and offered the choice to grant or
deny access to given origin.

Once their decision is made, their browser will receive a cookie remembering
this decision, and they will be redirected to the URL received in the "return"
field received upon above-described redirection.

Then, the application should retry the original request, which will be
accompanied by that cookie.

Backups
-------

Loosing the CA private key prevents issuing any new certificate trusted by
services which trusted the CA. Also, it prevents issuing any new CRL.
Recovering from such total loss requires starting a new CA and rolling it out
to all services which used the previous one. This is very time-costly.

So backups are required.

On the other hand, if someone gets their hand on the CA private key, they can
issue certificates for themselves, allowing them to authenticate with services
trusting the CA managed by caucase - including caucased itself if they issue a
user certificate: they can then revoke existing certificates and cause a lot of
damage.

So backups cannot happen in clear text, they must be encrypted.

But the danger of encrypted backups is that by definition they become worthless
if they cannot be decrypted. So as many (trusted) entities as possible should
be granted the ability to decrypt the backups.

The solution proposed by caucased is to encrypt produced backups in a way which
allows any of the caucase users to decrypt the archive.

As these users are already entrusted with issuing certificates, this puts
only a little more power in their hands than they already have. The little
extra power they get is that by having unrestricted access to the CA private
key they can issue certificates bypassing all caucase restrictions. The
proposed parade is to only make the backups available to a limited subset of
caucase users when there is an actual disaster, and otherwise keep it out of
their reach. This mechanism is not handled by caucase.

As there are few trusted users, caucase can keep their still-valid certificates
in its database for the duration of their validity with minimal size cost.

Backup procedure
----------------

Backups happen periodically as long as caucased is running. See
`--backup-period` and `--backup-directory`.

As discussed above, produced files should be kept out of reach of caucase
users until a disaster happens.

Restoration procedure
---------------------

See `caucased-manage --restore-backup`.

To restore, one of the trusted users must voluntarily compromise their own
private key, providing it to the administrator in charge of the restoration
procedure. Restoration procedure will hence immediately revoke their
certificate. They must also provide a CSR generated with a different private
key, so that caucase can provide them with a new certificate, so they keep
their access only via different credentials.

- admin identifies the list of keys which can decipher a backup, and broadcasts
  that list to key holders

- key holders manifest themselves

- admin picks a key holder, requests them to provide their existing private key
  and to generate a new key and accompanying CSR

- key holder provide requested items

- admin initiates restoration with `--restore-backup` and provides key holder
  with replacement certificate

- admin starts caucased, service is back online.

Backup file format
------------------

- 64bits: 'caucase\0' magic string

- 32bits LE: header length

- header: json-encoded header (see below)

- encrypted byte stream (aka payload)

Header schema (inspired from s/mime, but s/mime tools available do not
support at least iterative production or iterative generation)::

  {
    "description": "Caucase backup header",
    "required": ["algorithm", "key_list"],
    "properties": {
      "cipher": {
        "description": "Symetric ciher used for payload",
        "required": ["name"],
        "properties": {
          "name":
            "enum": ["aes256_cbc_pkcs7_hmac_10M_sha256"],
            "type": "string"
          },
          "parameter": {
            "description": "Name-dependend clear cipher parameter (ex: IV)",
            "type": "string"
          }
        }
        "type": "object"
      },
      "key_list": {
        "description": "Content key, encrypted with public keys",
        "minItems": 1,
        "items": {
          "required": ["id", "cipher", "key"],
          "properties": {
            "id": {
              "description": "Hex-encoded sha1 hash of the public key",
              "type": "string"
            },
            "cipher": {
              "description": "Asymetric cipher used for symetric key",
              "required": ["name"],
              "properties": {
                "name": {
                  "enum": ["rsa_oaep_sha1_mgf1_sha1"],
                  "type": "string"
                }
              },
              "type": "object"
            }
            "key": {
              "description": "Hex-encoded encrypted concatenation of signing and symetric encryption keys",
              "type": "string"
            }
          },
          "type": "object"
        },
        "type": "array"
      }
    },
    "type": "object"
  }
