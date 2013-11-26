# -*- coding: utf-8 -*-

from __future__ import absolute_import

# TODO: http://docs.python.org/2/library/xml.html#xml-vulnerabilities
from xml.etree.ElementTree import parse, ParseError, tostring
import sys

from httoop.codecs.common import Codec
from httoop.exceptions import DecodeError


class XML(Codec):
	mimetype = 'application/xml'

	def decode(self, data, charset=None):
		try:
			return parse(data)
		except ParseError:
			exc = sys.exc_info()
			raise DecodeError, exc[1], exc[2]

	def encode(self, root, charset=None):
		return tostring(root, charset)
