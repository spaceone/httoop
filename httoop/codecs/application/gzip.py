# -*- coding: utf-8 -*-

from httoop.codecs.common import Codec, Enconv
from httoop.exceptions import DecodeError, EncodeError

import zlib


class GZip(Codec):
	mimetype = 'application/gzip'

	@classmethod
	def encode(cls, data, charset=None):
		try:
			return zlib.compress(Enconv.encode(data, charset), 16 + zlib.MAX_WBITS)
		except zlib.error:
			raise EncodeError('Invalid gzip data')

	@classmethod
	def decode(cls, data, charset=None):
		try:
			data = zlib.decompress(data, 16 + zlib.MAX_WBITS)
		except zlib.error:
			raise DecodeError('Invalid gzip data')
		return Enconv.decode(data, charset)
