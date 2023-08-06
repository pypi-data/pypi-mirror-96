# This file is part of caucase
# Copyright (C) 2017-2020  Nexedi SA
#     Alain Takoudjou <alain.takoudjou@nexedi.com>
#     Vincent Pelletier <vincent@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
"""
Caucase - Certificate Authority for Users, Certificate Authority for SErvices
"""
from __future__ import absolute_import, print_function
import argparse
from binascii import hexlify
import datetime
import httplib
import json
import os
import socket
import struct
import sys
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from . import exceptions
from . import utils
from . import version
from .client import (
  CaucaseError,
  CaucaseClient,
  HTTPSOnlyCaucaseClient,
)

class RetryingCaucaseClient(CaucaseClient):
  """
  Similar to CaucaseClient, but retries indefinitely on http & socket errors.
  To use in long-lived processes where server may not be available yet, or is
  (hopefuly) temporarily unavailable, etc.

  Retries every 10 seconds.
  """
  _until = staticmethod(utils.until)
  _log_file = utils.toUnicodeWritableStream(sys.stdout)

  def _request(self, connection, method, url, body=None, headers=None):
    while True:
      try:
        return super(RetryingCaucaseClient, self)._request(
          connection=connection,
          method=method,
          url=url,
          body=body,
          headers=headers,
        )
      except (
        socket.error,
        # Note: all exceptions below inherit from httplib.HTTPException,
        # but so do errors which are either sign of code bugs
        # (ImproperConnectionState) or sign of garbage values provided by
        # caller/user, and these should be let through.
        httplib.BadStatusLine,
        httplib.LineTooLong,
        httplib.UnknownProtocol,
        httplib.IncompleteRead,
      ) as exception:
        connection.close() # Resets HTTPConnection state machine.
        # Note: repr(str(exception)) is nicer than repr(exception), without
        # letting non-printable characters through.
        next_try = datetime.datetime.utcnow() + datetime.timedelta(0, 10)
        print(
          u'Got a network error, retrying at %s, %s: %r' % (
            next_try.strftime(u'%Y-%m-%d %H:%M:%S +0000'),
            exception.__class__.__name__,
            unicode(exception),
          ),
          file=self._log_file,
        )
        self._until(next_try)

_cryptography_backend = default_backend()

STATUS_ERROR = 1
STATUS_WARNING = 2
STATUS_CALLBACK_ERROR = 3

MODE_SERVICE = 'service'
MODE_USER = 'user'

class CLICaucaseClient(object):
  """
  CLI functionalities
  """
  # Note: this class it more to reduce local variable scopes (avoiding
  # accidental mixups) in each methods than about API declaration.

  def __init__(self, client, stdout, stderr):
    self._client = client
    self._stdout = stdout
    self._stderr = stderr

  def _print(self, *args, **kw):
    kw.setdefault('file', self._stdout)
    print(*args, **kw)

  def putCSR(self, csr_path_list):
    """
    --send-csr
    """
    for csr_path in csr_path_list:
      csr_pem = utils.getCertRequest(csr_path)
      # Quick sanity check
      utils.load_certificate_request(csr_pem)
      self._print(
        self._client.createCertificateSigningRequest(csr_pem),
        csr_path,
      )

  def getCSR(self, csr_id_path_list):
    """
    --get-csr
    """
    for csr_id, csr_path in csr_id_path_list:
      csr_pem = self._client.getCertificateSigningRequest(int(csr_id))
      with open(csr_path, 'ab') as csr_file:
        csr_file.write(csr_pem)

  def getCRT(self, warning, error, crt_id_path_list, ca_list):
    """
    --get-crt
    """
    for crt_id, crt_path in crt_id_path_list:
      crt_id = int(crt_id)
      try:
        crt_pem = self._client.getCertificate(crt_id)
      except CaucaseError as e:
        if e.args[0] != httplib.NOT_FOUND:
          raise
        try:
          self._client.getCertificateSigningRequest(crt_id)
        except CaucaseError as e:
          if e.args[0] != httplib.NOT_FOUND:
            raise
          self._print(crt_id, 'not found - maybe CSR was rejected ?')
          error = True
        else:
          self._print(crt_id, 'CSR still pending')
          warning = True
      else:
        self._print(crt_id, end=' ')
        if utils.isCertificateAutoSigned(utils.load_certificate(
          crt_pem,
          ca_list,
          None,
        )):
          self._print('was (originally) automatically approved')
        else:
          self._print('was (originally) manually approved')
        if os.path.exists(crt_path):
          try:
            key_pem = utils.getKey(crt_path)
          except ValueError:
            self._print(
              'Expected to find exactly one privatekey key in %s, skipping' % (
                crt_path,
              ),
              file=self._stderr,
            )
            error = True
            continue
          try:
            utils.validateCertAndKey(crt_pem, key_pem)
          except ValueError:
            self._print(
              'Key in %s does not match retrieved certificate, skipping' % (
                crt_path,
              ),
              file=self._stderr,
            )
            error = True
            continue
        with open(crt_path, 'ab') as crt_file:
          crt_file.write(crt_pem)
    return warning, error

  def revokeCRT(self, error, crt_key_list):
    """
    --revoke-crt
    """
    for crt_path, key_path in crt_key_list:
      try:
        crt, key, _ = utils.getKeyPair(crt_path, key_path)
      except ValueError:
        self._print(
          'Could not find (exactly) one matching key pair in %s, skipping' % (
            [x for x in set((crt_path, key_path)) if x],
          ),
          file=self._stderr,
        )
        error = True
        continue
      self._client.revokeCertificate(crt, key)
    return error

  def renewCRT(
    self,
    crt_key_list,
    renewal_deadline,
    key_len,
    ca_certificate_list,
    updated,
    error,
  ):
    """
    --renew-crt
    """
    for crt_path, key_path in crt_key_list:
      try:
        old_crt_pem, old_key_pem, key_path = utils.getKeyPair(
          crt_path,
          key_path,
        )
      except ValueError:
        self._print(
          'Could not find (exactly) one matching key pair in %s, skipping' % (
            [x for x in set((crt_path, key_path)) if x],
          ),
          file=self._stderr,
        )
        error = True
        continue
      try:
        old_crt = utils.load_certificate(
          old_crt_pem,
          ca_certificate_list,
          None,
        )
      except exceptions.CertificateVerificationError:
        self._print(
          crt_path,
          'was not signed by this CA, revoked or otherwise invalid, skipping',
        )
        continue
      if renewal_deadline < old_crt.not_valid_after:
        self._print(crt_path, 'did not reach renew threshold, not renewing')
        continue
      new_key_pem, new_crt_pem = self._client.renewCertificate(
        old_crt=old_crt,
        old_key=utils.load_privatekey(old_key_pem),
        key_len=key_len,
      )
      if key_path is None:
        with open(crt_path, 'wb') as crt_file:
          crt_file.write(new_key_pem)
          crt_file.write(new_crt_pem)
      else:
        with open(
          crt_path,
          'wb',
        ) as crt_file, open(
          key_path,
          'wb',
        ) as key_file:
          key_file.write(new_key_pem)
          crt_file.write(new_crt_pem)
      updated = True
    return updated, error

  def listCSR(self, mode):
    """
    --list-csr
    """
    self._print('-- pending', mode, 'CSRs --')
    self._print(
      '%20s | %s' % (
        'csr_id',
        'subject preview (fetch csr and check full content !)',
      ),
    )
    for entry in self._client.getPendingCertificateRequestList():
      csr = utils.load_certificate_request(utils.toBytes(entry['csr']))
      self._print(
        '%20s | %r' % (
          entry['id'],
          repr(csr.subject),
        ),
      )
    self._print('-- end of pending', mode, 'CSRs --')

  def signCSR(self, csr_id_list):
    """
    --sign-csr
    """
    for csr_id in csr_id_list:
      self._client.createCertificate(int(utils.toUnicode(csr_id)))

  def signCSRWith(self, csr_id_path_list):
    """
    --sign-csr-with
    """
    for csr_id, csr_path in csr_id_path_list:
      self._client.createCertificate(
        int(utils.toUnicode(csr_id)),
        template_csr=utils.getCertRequest(csr_path),
      )

  def rejectCSR(self, csr_id_list):
    """
    --reject-csr
    """
    for csr_id in csr_id_list:
      self._client.deletePendingCertificateRequest(int(csr_id))

  def revokeOtherCRT(self, crt_list):
    """
    --revoke-other-crt
    """
    for crt_path in crt_list:
      try:
        # Note: also raises when there are serveral certs. This is intended:
        # revoking many certs from a single file seems a dubious use-case
        # (especially in the automated issuance context, which is supposed to
        # be caucase's main target), with high risk if carried without
        # questions (too many certificates revoked, or asingle unexpected one
        # among these, ...) and unambiguous solution is easy (if a human is
        # involved, as is likely the case, more or less directly, for
        # authenticated revocations).
        crt_pem = utils.getCert(crt_path)
      except ValueError:
        self._print(
          'Could not load a single certificate in %s, skipping' % (
            crt_path,
          ),
          file=self._stderr,
        )
      self._client.revokeCertificate(crt_pem)

  def revokeSerial(self, serial_list):
    """
    --revoke-serial
    """
    for serial in serial_list:
      self._client.revokeSerial(serial)

def main(argv=None, stdout=sys.stdout, stderr=sys.stderr):
  """
  Command line caucase client entry point.
  """
  parser = argparse.ArgumentParser(
    description='caucase',
  )
  parser.add_argument(
    '--version',
    action='version',
    version=version.__version__,
  )
  # XXX: currently, it is the server which chooses which digest is used to sign
  # stuff.
  # Should clients be able to tell it how to sign (and server could reject) ?
  parser.add_argument(
    '--ca-url',
    required=True,
    metavar='URL',
    help='caucase service HTTP base URL.',
  )
  parser.add_argument(
    '--ca-crt',
    default='cas.crt.pem',
    metavar='CRT_PATH',
    help='Services CA certificate file location. '
    'May be an existing directory or file, or non-existing. '
    'If non-existing and given path has an extension, a file will be created, '
    'otherwise a directory will be. '
    'When it is a file, it may contain multiple PEM-encoded concatenated '
    'certificates. When it is a directory, it may contain multiple files, '
    'each containing a single PEM-encoded certificate. '
    'default: %(default)s',
  )
  parser.add_argument(
    '--user-ca-crt',
    default='cau.crt.pem',
    metavar='CRT_PATH',
    help='Users CA certificate file location. '
    'May be an existing directory or file, or non-existing. '
    'If non-existing and given path has an extension, a file will be created, '
    'otherwise a directory will be. '
    'When it is a file, it may contain multiple PEM-encoded concatenated '
    'certificates. When it is a directory, it may contain multiple files, '
    'each containing a single PEM-encoded certificate. '
    'default: %(default)s',
  )
  parser.add_argument(
    '--crl',
    default='cas.crl.pem',
    metavar='CRL_PATH',
    help='Services certificate revocation list location. '
    'May be an existing directory or file, or non-existing. '
    'If non-existing and given path has an extension, a file will be created, '
    'otherwise a directory will be. '
    'When it is a file, it may contain multiple PEM-encoded concatenated '
    'CRLs. When it is a directory, it may contain multiple files, each '
    'containing a single PEM-encoded CRL. '
    'default: %(default)s',
  )
  parser.add_argument(
    '--user-crl',
    default='cau.crl.pem',
    metavar='CRL_PATH',
    help='Users certificate revocation list location. '
    'May be an existing directory or file, or non-existing. '
    'If non-existing and given path has an extension, a file will be created, '
    'otherwise a directory will be. '
    'When it is a file, it may contain multiple PEM-encoded concatenated '
    'CRLs. When it is a directory, it may contain multiple files, each '
    'containing a single PEM-encoded CRL. '
    'default: %(default)s',
  )
  parser.add_argument(
    '--threshold',
    default=31,
    type=float,
    help='The remaining certificate validity period, in days, under '
    'which a renew is desired. default: %(default)s',
  )
  parser.add_argument(
    '--key-len',
    default=2048,
    type=int,
    metavar='BITLENGTH',
    help='Number of bits to use when generating a new private key. '
    'default: %(default)s',
  )
  parser.add_argument(
    '--on-renew',
    metavar='EXECUTABLE_PATH',
    help='Path of an executable file to call after any renewal (CA cert, '
    'certificate, revocation list).',
  )
  parser.add_argument(
    '--user-key',
    metavar='KEY_PATH',
    help='User private key and certificate bundled in a single file to '
    'authenticate with caucase.',
  )
  parser.add_argument(
    '--mode',
    default=MODE_SERVICE,
    choices=[MODE_SERVICE, MODE_USER],
    help='The type of certificates you want to manipulate: '
    '<%s> certificates allow managing caucase server, '
    '<%s> certificates can be validated by caucase\'s CA certificate. '
    'default: %%(default)s' % (
      MODE_USER,
      MODE_SERVICE,
    )
  )

  anonymous_group = parser.add_argument_group(
    'Anonymous actions',
    'Actions which do no require authentication.',
  )
  anonymous_group.add_argument(
    '--send-csr',
    nargs='+',
    metavar='CSR_PATH',
    default=[],
    help='Request signature of these certificate signing requests.',
  )
  anonymous_group.add_argument(
    '--get-crt',
    nargs=2,
    action='append',
    default=[],
    metavar=('CSR_ID', 'CRT_PATH'),
    help='Retrieve the certificate identified by '
    'identifier and store it at given path. '
    'If CRT_PATH exists and contains the private key corresponding to '
    'received certificate, certificate will be appended to that file. '
    'Can be given multiple times.',
  )
  anonymous_group.add_argument(
    '--revoke-crt',
    nargs=2,
    action='append',
    default=[],
    metavar=('CRT_PATH', 'KEY_PATH'),
    help='Revoke certificate. If CRT_PATH file contains both a certificate '
    'and a key, KEY_PATH is ignored. '
    'Can be given multiple times.',
  )
  anonymous_group.add_argument(
    '--renew-crt',
    nargs=2,
    default=[],
    action='append',
    metavar=('CRT_PATH', 'KEY_PATH'),
    help='Renew certificates in-place if they exceed THRESHOLD. '
    'If CRT_PATH file contains both certificate and key, KEY_PATH is ignored '
    'and CRT_PATH receives both the new key and the new certificate. '
    'Can be given multiple times.',
  )
  anonymous_group.add_argument(
    '--get-csr',
    nargs=2,
    default=[],
    action='append',
    metavar=('CSR_ID', 'CSR_PATH'),
    help='Retrieve certificate signing request and append to CSR_PATH. '
    'Should only be needed before deciding to sign or reject the request. '
    'Can be given multiple times.',
  )
  anonymous_group.add_argument(
    '--update-user',
    action='store_true',
    help='Update or create user CA and CRL. '
    'Should only be needed by the https server in front of caucase.'
  )

  authenticated_group = parser.add_argument_group(
    'Authenticated actions',
    'Actions which require an authentication. Requires --user-key .',
  )
  authenticated_group.add_argument(
    '--list-csr',
    action='store_true',
    help='List certificate signing requests currently pending on server.',
  )
  authenticated_group.add_argument(
    '--sign-csr',
    nargs='+',
    default=[],
    metavar='CSR_ID',
    help='Sign pending certificate signing requests.',
  )
  authenticated_group.add_argument(
    '--sign-csr-with',
    nargs=2,
    default=[],
    action='append',
    metavar=('CSR_ID', 'CSR_PATH'),
    help='Sign pending certificate signing request, but use provided CSR for '
    'requested subject and extensions instead of stored CSR. '
    'Can be given multiple times.',
  )
  authenticated_group.add_argument(
    '--reject-csr',
    nargs='+',
    default=[],
    metavar='CSR_ID',
    help='Reject these pending certificate signing requests.',
  )
  authenticated_group.add_argument(
    '--revoke-other-crt',
    nargs='+',
    default=[],
    metavar='CRT_PATH',
    help='Revoke certificate without needing access to their private key.'
  )
  authenticated_group.add_argument(
    '--revoke-serial',
    nargs='+',
    default=[],
    metavar='SERIAL',
    type=int,
    help='Revoke certificate by serial number, without needing the '
    'certificate at all. DANGEROUS: typos will not be detected ! '
    'COSTLY: revocation will stay in the revocation list until all '
    'currently valid CA certificates have expired. '
    'Use --revoke and --revoke-other-crt whenever possible.',
  )
  args = parser.parse_args(argv)
  stdout = utils.toUnicodeWritableStream(stdout)
  stderr = utils.toUnicodeWritableStream(stderr)

  sign_csr_id_set = set(args.sign_csr)
  sign_with_csr_id_set = {x for x, _ in args.sign_csr_with}
  if (
    sign_csr_id_set.intersection(args.reject_csr) or
    sign_with_csr_id_set.intersection(args.reject_csr) or
    sign_csr_id_set.intersection(sign_with_csr_id_set)
  ):
    print(
      'A given CSR_ID cannot be in more than one of --sign-csr, '
      '--sign-csr-with and --reject-csr',
      file=stderr,
    )
    raise SystemExit(STATUS_ERROR)

  updated = False
  warning = False
  error = False
  finished = False
  cau_url = args.ca_url + '/cau'
  cas_url = args.ca_url + '/cas'

  try:
    # Get a working, up-to-date CAS CA certificate file.
    updated |= CaucaseClient.updateCAFile(cas_url, args.ca_crt)
    # --update-user, CA part
    if args.update_user or args.mode == MODE_USER:
      updated |= CaucaseClient.updateCAFile(cau_url, args.user_ca_crt)

    client = CLICaucaseClient(
      client=CaucaseClient(
        ca_url={
          MODE_SERVICE: cas_url,
          MODE_USER: cau_url,
        }[args.mode],
        ca_crt_pem_list=utils.getCertList(args.ca_crt),
        user_key=args.user_key,
      ),
      stdout=stdout,
      stderr=stderr,
    )
    ca_list = [
      utils.load_ca_certificate(x)
      for x in utils.getCertList({
        MODE_SERVICE: args.ca_crt,
        MODE_USER: args.user_ca_crt,
      }[args.mode])
    ]
    client.putCSR(args.send_csr)
    client.getCSR(args.get_csr)
    warning, error = client.getCRT(warning, error, args.get_crt, ca_list)
    error = client.revokeCRT(error, args.revoke_crt)
    updated, error = client.renewCRT(
      crt_key_list=args.renew_crt,
      renewal_deadline=datetime.datetime.utcnow() + datetime.timedelta(
        args.threshold,
        0,
      ),
      key_len=args.key_len,
      ca_certificate_list=ca_list,
      updated=updated,
      error=error,
    )
    client.signCSR(args.sign_csr)
    client.signCSRWith(args.sign_csr_with)
    client.rejectCSR(args.reject_csr)
    client.revokeOtherCRT(args.revoke_other_crt)
    client.revokeSerial(args.revoke_serial)
    # show latest CSR list status
    if args.list_csr:
      client.listCSR(args.mode)
    # update our CRL after all revocations we were requested
    updated |= CaucaseClient.updateCRLFile(cas_url, args.crl, [
      utils.load_ca_certificate(x)
      for x in utils.getCertList(args.ca_crt)
    ])
    # --update-user, CRL part
    if args.update_user:
      updated |= CaucaseClient.updateCRLFile(cau_url, args.user_crl, [
        utils.load_ca_certificate(x)
        for x in utils.getCertList(args.user_ca_crt)
      ])
    finished = True
  finally:
    if updated and args.on_renew:
      status = os.system(args.on_renew)
      # Avoid raising if we arrived here because of an exception, to not hide
      # the original problem.
      if finished and status:
        raise SystemExit(STATUS_CALLBACK_ERROR)
  if error:
    raise SystemExit(STATUS_ERROR)
  if warning:
    raise SystemExit(STATUS_WARNING)

def probe(argv=None):
  """
  Verify basic caucase server functionality
  """
  parser = argparse.ArgumentParser(
    description='caucase probe - Verify basic caucase server functionality',
  )
  parser.add_argument(
    '--version',
    action='version',
    version=version.__version__,
  )
  parser.add_argument(
    'ca_url',
    nargs=1,
    help='caucase service HTTP base URL.',
  )
  ca_url, = parser.parse_args(argv).ca_url
  cas_url = ca_url + '/cas'
  http_client = CaucaseClient(
    ca_url=cas_url,
  )
  http_ca_pem = http_client.getCACertificate()
  https_ca_pem = HTTPSOnlyCaucaseClient(
    ca_url=cas_url,
    ca_crt_pem_list=[http_ca_pem],
  ).getCACertificate()
  # Retrieve again in case there was a renewal between both calls - we do
  # not expect 2 renewals in very short succession.
  http2_ca_pem = http_client.getCACertificate()
  if https_ca_pem not in (http_ca_pem, http2_ca_pem):
    raise ValueError('http and https do not serve the same caucase database')

def updater(argv=None, until=utils.until):
  """
  Bootstrap certificate and companion files and keep them up-to-date.
  """
  parser = argparse.ArgumentParser(
    description='caucase updater - '
    'Bootstrap certificate and companion files and keep them up-to-date',
  )
  parser.add_argument(
    '--version',
    action='version',
    version=version.__version__,
  )
  parser.add_argument(
    '--ca-url',
    required=True,
    metavar='URL',
    help='caucase service HTTP base URL.',
  )
  parser.add_argument(
    '--cas-ca',
    required=True,
    metavar='CRT_PATH',
    help='Service CA certificate file location used to verify connection '
    'to caucase. '
    'May be an existing directory or file, or non-existing. '
    'If non-existing and given path has an extension, a file will be created, '
    'otherwise a directory will be. '
    'When it is a file, it may contain multiple PEM-encoded concatenated '
    'certificates. When it is a directory, it may contain multiple files, '
    'each containing a single PEM-encoded certificate. '
    'Will be maintained up-to-date.',
  )
  parser.add_argument(
    '--threshold',
    default=31,
    type=float,
    help='The remaining certificate validity period, in days, under '
    'which a renew is desired. default: %(default)s',
  )
  parser.add_argument(
    '--crl-threshold',
    default=7,
    type=float,
    help='The remaining certificate revocation validity period, in days, '
    'under which a new one is requested. default: %(default)s',
  )
  parser.add_argument(
    '--key-len',
    default=2048,
    type=int,
    metavar='BITLENGTH',
    help='Number of bits to use when generating a new private key. '
    'default: %(default)s',
  )
  parser.add_argument(
    '--on-renew',
    metavar='EXECUTABLE_PATH',
    help='Path of an executable file to call after any renewal (CA cert, '
    'certificate, revocation list).',
  )
  parser.add_argument(
    '--max-sleep',
    default=31,
    type=float,
    help='Maximum number of days to sleep for. Allows refreshing the CRL '
    'more often on sensitive services. default: %(default)s',
  )
  parser.add_argument(
    '--mode',
    default=MODE_SERVICE,
    choices=[MODE_SERVICE, MODE_USER],
    help='The type of certificates you want to manipulate: '
    '<%s> certificates allow managing caucase server, '
    '<%s> certificates can be validated by caucase\'s CA certificate. '
    'default: %%(default)s' % (
      MODE_USER,
      MODE_SERVICE,
    )
  )
  parser.add_argument(
    '--csr',
    metavar='CSR_PATH',
    help='Path of your CSR to use for initial request of a certificate for '
    'MODE. Ignored once a certificate exists at the location given by '
    '--crt .',
  )
  parser.add_argument(
    '--key',
    metavar='KEY_PATH',
    help='Path of your private key file. Must always exist when this command '
    'is started. Will be updated on certificate renewal. If not provided, '
    'both key and certificate will be stored in the file pointed at by '
    '--crt .',
  )
  parser.add_argument(
    '--crt',
    metavar='CRT_PATH',
    help='Path of your certificate for MODE. Will be renewed before '
    'expiration.',
  )
  parser.add_argument(
    '--ca',
    required=True,
    metavar='CRT_PATH',
    help='Path of your CA certificate for MODE. '
    'May be an existing directory or file, or non-existing. '
    'If non-existing and given path has an extension, a file will be created, '
    'otherwise a directory will be. '
    'When it is a file, it may contain multiple PEM-encoded concatenated '
    'certificates. When it is a directory, it may contain multiple files, '
    'each containing a single PEM-encoded certificate. '
    'Will be maintained up-to-date.',
  )
  parser.add_argument(
    '--crl',
    required=True,
    metavar='CRT_PATH',
    help='Path of your certificate revocation list for MODE. '
    'May be an existing directory or file, or non-existing. '
    'If non-existing and given path has an extension, a file will be created, '
    'otherwise a directory will be. '
    'When it is a file, it may contain multiple PEM-encoded concatenated '
    'CRLs. When it is a directory, it may contain multiple files, each '
    'containing a single PEM-encoded CRL. '
    'Will be maintained up-to-date.'
  )
  args = parser.parse_args(argv)
  try:
    cas_url = args.ca_url + '/cas'
    ca_url = {
      MODE_SERVICE: cas_url,
      MODE_USER: args.ca_url + '/cau',
    }[args.mode]
    threshold = datetime.timedelta(args.threshold, 0)
    crl_threshold = datetime.timedelta(args.crl_threshold, 0)
    max_sleep = datetime.timedelta(args.max_sleep, 0)
    min_sleep = datetime.timedelta(0, 60)
    updated = RetryingCaucaseClient.updateCAFile(
      cas_url,
      args.cas_ca,
    ) and args.cas_ca == args.ca
    client = RetryingCaucaseClient(
      ca_url=ca_url,
      ca_crt_pem_list=utils.getCertList(args.cas_ca)
    )
    if args.crt and not utils.hasOneCert(args.crt):
      print('Bootstraping...')
      csr_pem = utils.getCertRequest(args.csr)
      # Quick sanity check before bothering server
      utils.load_certificate_request(csr_pem)
      csr_id = client.createCertificateSigningRequest(csr_pem)
      print('Waiting for signature of', csr_id)
      while True:
        try:
          crt_pem = client.getCertificate(csr_id)
        except CaucaseError as e:
          if e.args[0] != httplib.NOT_FOUND:
            raise
          # If server does not know our CSR anymore, getCSR will raise.
          # If it does, we were likely rejected, so exit by letting exception
          # through.
          client.getCertificateSigningRequest(csr_id)
          # Still here ? Ok, wait a bit and try again.
          until(datetime.datetime.utcnow() + datetime.timedelta(0, 60))
        else:
          with open(args.crt, 'ab') as crt_file:
            crt_file.write(crt_pem)
          updated = True
          break
      print('Bootstrap done')
    next_deadline = datetime.datetime.utcnow()
    while True:
      print(
        'Next wake-up at',
        next_deadline.strftime('%Y-%m-%d %H:%M:%S +0000'),
      )
      now = until(next_deadline)
      next_deadline = now + max_sleep
      if args.cas_ca != args.ca and RetryingCaucaseClient.updateCAFile(
        cas_url,
        args.cas_ca,
      ):
        client = RetryingCaucaseClient(
          ca_url=ca_url,
          ca_crt_pem_list=utils.getCertList(args.cas_ca)
        )
      if RetryingCaucaseClient.updateCAFile(ca_url, args.ca):
        print('Got new CA')
        updated = True
        # Note: CRL expiration should happen several time during CA renewal
        # period, so it should not be needed to keep track of CA expiration
        # for next deadline.
      ca_crt_list = [
        utils.load_ca_certificate(x)
        for x in utils.getCertList(args.ca)
      ]
      if RetryingCaucaseClient.updateCRLFile(ca_url, args.crl, ca_crt_list):
        print('Got new CRL')
        updated = True
      for crl_pem in utils.getCRLList(args.crl):
        next_deadline = min(
          next_deadline,
          utils.load_crl(
            crl_pem,
            ca_crt_list,
          ).next_update - crl_threshold,
        )
      if args.crt:
        crt_pem, key_pem, key_path = utils.getKeyPair(args.crt, args.key)
        crt = utils.load_certificate(crt_pem, ca_crt_list, None)
        if crt.not_valid_after - threshold <= now:
          print('Renewing', args.crt)
          new_key_pem, new_crt_pem = client.renewCertificate(
            old_crt=crt,
            old_key=utils.load_privatekey(key_pem),
            key_len=args.key_len,
          )
          if key_path is None:
            with open(args.crt, 'wb') as crt_file:
              crt_file.write(new_key_pem)
              crt_file.write(new_crt_pem)
          else:
            with open(
              args.crt,
              'wb',
            ) as crt_file, open(
              key_path,
              'wb',
            ) as key_file:
              key_file.write(new_key_pem)
              crt_file.write(new_crt_pem)
          crt = utils.load_certificate(utils.getCert(args.crt), ca_crt_list, None)
          updated = True
        next_deadline = min(
          next_deadline,
          crt.not_valid_after - threshold,
        )
      next_deadline = max(
        next_deadline,
        now + min_sleep,
      )
      if updated:
        if args.on_renew is not None:
          status = os.system(args.on_renew)
          if status:
            print('Renewal hook exited with status:', status, file=sys.stderr)
            raise SystemExit(STATUS_ERROR)
        updated = False
  except (utils.SleepInterrupt, SystemExit):
    # Not intercepting KeyboardInterrupt so interrupting outside of
    # interruptibleSleep shows where the script got interrupted.
    pass

def rerequest(argv=None):
  """
  Produce a new private key and sign a CSR created by copying an existing,
  well-signed CSR.
  """
  parser = argparse.ArgumentParser(
    description='caucase rerequest - '
    'Produce a new private key and sign a CSR created by copying an existing, '
    'well-signed CSR.',
  )
  parser.add_argument(
    '--version',
    action='version',
    version=version.__version__,
  )
  parser.add_argument(
    '--template',
    required=True,
    help='Existing PEM-encodd CSR to use as a template.',
  )
  parser.add_argument(
    '--csr',
    required=True,
    help='Path of produced PEM-encoded CSR.',
  )
  parser.add_argument(
    '--key',
    required=True,
    help='Path of produced PEM-encoded private key.',
  )
  parser.add_argument(
    '--key-len',
    default=2048,
    type=int,
    metavar='BITLENGTH',
    help='Number of bits to use when generating a new private key. '
    'default: %(default)s',
  )
  args = parser.parse_args(argv)
  template = utils.load_certificate_request(
    utils.getCertRequest(args.template),
  )
  key = utils.generatePrivateKey(key_len=args.key_len)
  csr_pem = utils.dump_certificate_request(
    x509.CertificateSigningRequestBuilder(
      subject_name=template.subject,
      extensions=template.extensions,
    ).sign(
      private_key=key,
      algorithm=utils.DEFAULT_DIGEST_CLASS(),
      backend=_cryptography_backend,
    ),
  )
  key_pem = utils.dump_privatekey(key)
  orig_umask = os.umask(0o177)
  try:
    with open(args.key, 'wb') as key_file:
      key_file.write(key_pem)
  finally:
    os.umask(orig_umask)
  with open(args.csr, 'wb') as csr_file:
    csr_file.write(csr_pem)

def key_id(argv=None, stdout=sys.stdout):
  """
  Displays key identifier from private key, and the list of acceptable key
  identifiers for a given backup file.
  """
  parser = argparse.ArgumentParser(
    description='caucase key id - '
    'Displays key identifier from private key, and the list of acceptable key'
    'identifiers for a given backup file.',
  )
  parser.add_argument(
    '--version',
    action='version',
    version=version.__version__,
  )
  parser.add_argument(
    '--private-key',
    nargs='+',
    default=(),
    help='PEM-encoded keys to display the identifier of.',
  )
  parser.add_argument(
    '--backup',
    nargs='+',
    default=(),
    help='Caucase backup files to display acceptable deciphering key '
    'identifiers of.',
  )
  args = parser.parse_args(argv)
  stdout = utils.toUnicodeWritableStream(stdout)
  for key_path in args.private_key:
    with open(key_path, 'rb') as key_file:
      print(
        key_path,
        hexlify(
          x509.SubjectKeyIdentifier.from_public_key(
            utils.load_privatekey(key_file.read()).public_key(),
          ).digest,
        ),
        file=stdout,
      )
  for backup_path in args.backup:
    print(backup_path, file=stdout)
    with open(backup_path, 'rb') as backup_file:
      magic = backup_file.read(8)
      if magic != b'caucase\0':
        raise ValueError('Invalid backup magic string')
      header_len, = struct.unpack(
        '<I',
        backup_file.read(struct.calcsize('<I')),
      )
      for key_entry in json.loads(backup_file.read(header_len))['key_list']:
        print(' ', key_entry['id'].encode('utf-8'), file=stdout)
