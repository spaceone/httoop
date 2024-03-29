# -*- coding: utf-8 -*-

from binascii import Error as Base64Error
from typing import Dict, Union

from httoop.exceptions import InvalidHeader
from httoop.header.element import HeaderElement
from httoop.util import ByteUnicodeDict, _, decode_base64, encode_base64


class BasicAuthRequestScheme(object):

	@staticmethod
	def parse(authinfo: bytes) -> Dict[str, bytes]:
		#try:
		#	authinfo = authinfo.encode('ascii')
		#except ValueError:
		#	raise InvalidHeader(_(u'Invalid base64 in basic authentication'))

		try:
			username, password = decode_base64(authinfo.strip()).split(b':')
		except Base64Error:
			raise InvalidHeader(_(u'Basic authentication contains invalid base64'))
		except ValueError:
			raise InvalidHeader(_(u'No username:password provided'))

		authinfo = {
			#'username': username.decode('ISO8859-1'),
			#'password': password.decode('ISO8859-1')
			'username': username,
			'password': password,
		}
		return authinfo

	@staticmethod
	def compose(authinfo: ByteUnicodeDict) -> bytes:
		username = authinfo['username']
		password = authinfo['password']
		#username = username.encode('ISO8859-1')
		#password = password.encode('ISO8859-1')
		return encode_base64(b'%s:%s' % (username, password)).strip()


class BasicAuthResponseScheme(object):

	@staticmethod
	def parse(authinfo: bytes) -> Dict[bytes, Union[str, bytes]]:
		params = HeaderElement.parseparams(b'X;%s' % authinfo)[1]
		params.setdefault(b'realm', b'')
		return params

	@staticmethod
	def compose(authinfo: ByteUnicodeDict) -> bytes:
		return HeaderElement.formatparam(b'realm', authinfo['realm'], True)
