# -*- coding: utf-8 -*-

from __future__ import absolute_import

# TODO: http://docs.python.org/2/library/xml.html#xml-vulnerabilities
from xml.etree.ElementTree import parse, ParseError, tostring

from httoop.codecs.codec import Codec
from httoop.exceptions import DecodeError


class XML(Codec):
	mimetype = 'application/xml'

	def decode(self, data, charset=None, mimetype=None):
		try:
			return parse(data)
		except ParseError as exc:
			raise DecodeError(u'Could not decode as %s: %s' % (self.mimetype, exc,))

	def encode(self, root, charset=None, mimetype=None):
		return tostring(root, charset)
