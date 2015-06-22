# -*- coding: utf-8 -*-
import re

from httoop.header.element import HeaderElement
from httoop.exceptions import InvalidHeader

from httoop.authentication.basic import BasicAuthRequestScheme, BasicAuthResponseScheme
from httoop.authentication.digest import DigestAuthResponseScheme, DigestAuthRequestScheme


class AuthElement(HeaderElement):

	schemes = {}
	RE_SPACE_SPLIT = re.compile(br'\s+(?=(?:[^"]*"[^"]*")*[^"]*$)')

	@classmethod
	def parseparams(cls, elementstr):
		try:
			scheme, authinfo = elementstr.split(b' ', 1)
		except ValueError:
			raise InvalidHeader(u'Authorization headers must contain authentication scheme')
		try:
			parser = cls.schemes[scheme.lower()]
		except KeyError:
			raise InvalidHeader(u'Unsupported authentication scheme: %r' % (scheme,))

		try:
			authinfo = parser.parse(authinfo)
		except KeyError as key:
			raise InvalidHeader(u'Missing parameter %r for authentication scheme %r' % (str(key), scheme))

		return scheme.title(), authinfo

	def compose(self):
		try:
			scheme = self.schemes[self.value.lower()]
		except KeyError:
			raise InvalidHeader(u'Unsupported authentication scheme: %r' % (self.value,))

		try:
			authinfo = scheme.compose(self.params)
		except KeyError as key:
			raise InvalidHeader(u'Missing parameter %r for authentication scheme %r' % (str(key), self.value))

		return b'%s %s' % (self.value.title(), authinfo)

	@classmethod
	def split(cls, value):
		value = cls.RE_SPACE_SPLIT.split(value)
		indexes = [i for i, val in enumerate(value) if val != b',' and b'=' not in val]
		return [b' '.join(value[a:b]) for a, b in zip(indexes, indexes[1:] + [None])]


class AuthRequestElement(AuthElement):

	schemes = {
		'basic': BasicAuthRequestScheme,
		'digest': DigestAuthRequestScheme
	}


class AuthResponseElement(AuthElement):

	schemes = {
		'basic': BasicAuthResponseScheme,
		'digest': DigestAuthResponseScheme
	}

	# TODO: sort by security

	@property
	def realm(self):
		return self.params.get('realm')

	@realm.setter
	def realm(self, realm):
		self.params['realm'] = realm.replace('"', '')


class AuthInfoElement(HeaderElement):
	pass
