# -*- coding: utf-8 -*-
import re
from typing import Any, Dict, List, Tuple, Union

from httoop.authentication.basic import BasicAuthRequestScheme, BasicAuthResponseScheme
from httoop.authentication.digest import DigestAuthRequestScheme, DigestAuthResponseScheme
from httoop.exceptions import InvalidHeader
from httoop.header.element import HeaderElement
from httoop.util import _


class AuthElement(HeaderElement):

	schemes = {}
	RE_SPACE_SPLIT = re.compile(br'\s+(?=(?:[^"]*"[^"]*")*[^"]*$)')

	def sanitize(self) -> None:
		for key, value in list(self.params.items()):
			if not isinstance(value, bytes) and isinstance(value, str):
				self.params[key] = value.encode('UTF-8')
			elif isinstance(value, (list, tuple)):
				self.params[key] = type(value)(x.encode('UTF-8') if not isinstance(x, bytes) and isinstance(x, str) else x for x in value)

	@classmethod
	def parseparams(cls, elementstr: bytes) -> Union[Tuple[bytes, Dict[bytes, str]], Tuple[bytes, Dict[str, bytes]], Tuple[bytes, Dict[str, Union[bytes, List[bytes], bool]]], Tuple[bytes, Dict[str, Union[bytes, List[bytes]]]], Tuple[bytes, Dict[bytes, Union[str, bytes]]]]:
		try:
			scheme, authinfo = elementstr.split(b' ', 1)
		except ValueError:
			raise InvalidHeader(_(u'Authorization headers must contain authentication scheme'))
		try:
			parser = cls.schemes[scheme.decode('ISO8859-1').lower()]
		except KeyError:
			raise InvalidHeader(_(u'Unsupported authentication scheme: %r'), scheme)

		try:
			authinfo = parser.parse(authinfo)
		except KeyError as key:
			raise InvalidHeader(_(u'Missing parameter %r for authentication scheme %r'), str(key), scheme)

		return scheme.title(), authinfo

	def compose(self) -> bytes:
		try:
			scheme = self.schemes[self.value.lower()]
		except KeyError:
			raise InvalidHeader(_(u'Unsupported authentication scheme: %r'), self.value)

		try:
			authinfo = scheme.compose(self.params)
		except KeyError as key:
			raise InvalidHeader(_(u'Missing parameter %r for authentication scheme %r'), str(key), self.value)

		return b'%s %s' % (self.value.encode('ASCII').title(), authinfo)

	@classmethod
	def split(cls, value: bytes) -> List[Union[bytes, Any]]:
		value = cls.RE_SPACE_SPLIT.split(value)
		indexes = [i for i, val in enumerate(value) if val != b',' and b'=' not in val]
		return [b' '.join(value[a:b]) for a, b in zip(indexes, indexes[1:] + [None])]


class AuthRequestElement(AuthElement):

	encoding = 'ASCII'

	schemes = {
		'basic': BasicAuthRequestScheme,
		'digest': DigestAuthRequestScheme
	}

	@property
	def scheme(self):
		return self.value.lower()

	@property
	def username(self):
		return self.params.get('username').decode(self.encoding)

	@username.setter
	def username(self, username):
		self.params['username'] = username.encode(self.encoding)

	@property
	def password(self):
		if self.scheme == 'basic':
			return self.params.get('password').decode(self.encoding)

	@password.setter
	def password(self, password):
		if self.scheme == 'basic':
			self.params['password'] = password.encode(self.encoding)


class AuthResponseElement(AuthElement):

	schemes = {
		'basic': BasicAuthResponseScheme,
		'digest': DigestAuthResponseScheme
	}

	@classmethod
	def sorted(cls, elements: List[Union["WWWAuthenticate", Any]]) -> List[Union["WWWAuthenticate", Any]]:
		return list(sorted(elements, key=lambda e: {'basic': u'\xff'}.get(e.value.lower(), e.value)))

	@classmethod
	def join(cls, values: List[bytes]) -> bytes:
		return b' '.join(values)

	@property
	def realm(self):
		return self.params[b'realm'].decode('ASCII')

	@realm.setter
	def realm(self, realm):
		self.params['realm'] = realm.replace(u'"', u'').encode('ASCII', 'ignore')


class AuthInfoElement(HeaderElement):
	pass
