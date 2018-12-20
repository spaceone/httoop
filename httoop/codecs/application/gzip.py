# -*- coding: utf-8 -*-

from __future__ import absolute_import

from httoop.codecs.codec import Codec
from httoop.exceptions import DecodeError, EncodeError
from httoop.util import _

import zlib


class GZip(Codec):
	mimetype = 'application/gzip'

	compression_level = 6

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):
		try:
			return zlib.compress(Codec.encode(data, charset), cls.compression_level)
		except zlib.error:
			raise EncodeError(_(u'Invalid gzip data.'))

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):
		try:
			data = zlib.decompress(data, 16 + zlib.MAX_WBITS)
		except zlib.error:
			raise DecodeError(_(u'Invalid gzip data.'))
		return Codec.decode(data, charset)
