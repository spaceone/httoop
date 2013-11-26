# -*- coding: utf-8 -*-

from httoop.codecs.common import Codec, Enconv
from httoop.exceptions import DecodeError, EncodeError

import zlib


class Deflate(Codec):
	mimetype = 'application/zlib'

	@classmethod
	def encode(cls, data, charset=None):
		try:
			return zlib.compress(Enconv.encode(data, charset))
		except zlib.error:
			raise EncodeError('Invalid zlib/deflate data')

	@classmethod
	def decode(cls, data, charset=None):
		try:
			data = zlib.decompress(data)
		except zlib.error:
			raise DecodeError('Invalid zlib/deflate data')
		return Enconv.decode(data, charset)
