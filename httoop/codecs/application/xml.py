# -*- coding: utf-8 -*-

from __future__ import absolute_import

# TODO: http://docs.python.org/2/library/xml.html#xml-vulnerabilities
# TODO: https://www.owasp.org/index.php/XML_External_Entity_%28XXE%29_Processing
try:
	from defusedxml.ElementTree import ParseError, fromstring, tostring
except ImportError:  # pragma: no cover
	# TODO: emit a warning
	from xml.etree.ElementTree import ParseError, tostring  # nosec

	def fromstring(data):
		raise ParseError('Will not parse without defusedxml!')


from httoop.codecs.codec import Codec
from httoop.exceptions import DecodeError


class XML(Codec):
	mimetype = 'application/xml'

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):
		try:
			return fromstring(data)
		except ParseError as exc:
			raise DecodeError(u'Could not decode as %s: %s' % (mimetype, exc,))

	@classmethod
	def encode(cls, root, charset=None, mimetype=None):
		return tostring(root, charset)
