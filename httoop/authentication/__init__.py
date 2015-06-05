# -*- coding: utf-8 -*-

from httoop.header.element import HeaderElement
from httoop.exceptions import InvalidHeader
from httoop.util import iteritems


class AuthElement(HeaderElement):

	schemes = {}

	@classmethod
	def parseparams(cls, elementstr):
		try:
			scheme, authinfo = elementstr.split(b' ', 1)
		except ValueError:
			raise InvalidHeader(u'Authorization headers must contain authentication scheme')
		scheme = scheme.lower()
		try:
			parser = cls.schemes[scheme]
		except KeyError:
			raise InvalidHeader(u'Unsupported authentication scheme: %r' % (scheme,))

		authinfo = parser.parse(authinfo)
		return scheme, authinfo

	def compose(self):
		params = [b', %s' % self.formatparam(k, v) for k, v in iteritems(self.params)]
		return b'%s%s' % (self.value.title(), ''.join(params))


class AuthRequestElement(AuthElement):

	schemes = {
#		'basic': BasicAuthRequestScheme,
#		'digest': DigestAuthRequestScheme
	}


class AuthResponseElement(AuthElement):

	schemes = {
#		'basic': BasicAuthResponseScheme,
#		'digest': DigestAuthResponseScheme
	}

	# TODO: sort by security

	@staticmethod
	def split(value):
		value = value.split()
		indexes = [i for i, val in enumerate(value) if val != b',' and b'=' not in val]
		return [b' '.join(value[a:b]) for a, b in zip(indexes, indexes[1:] + [None])]


class AuthInfoElement(HeaderElement):
	pass
