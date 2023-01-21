# -*- coding: utf-8 -*-

from __future__ import absolute_import

import zlib
from typing import Optional

from httoop.codecs.codec import Codec
from httoop.exceptions import DecodeError, EncodeError
from httoop.util import _


class Deflate(Codec):
	mimetype = 'application/zlib'

	@classmethod
	def encode(cls, data: bytes, charset: None=None, mimetype: None=None) -> bytes:
		try:
			return zlib.compress(Codec.encode(data, charset))
		except zlib.error:  # pragma: no cover
			raise EncodeError(_(u'Invalid zlib/deflate data.'))

	@classmethod
	def decode(cls, data: bytes, charset: Optional[str]=None, mimetype: None=None) -> str:
		try:
			data = zlib.decompress(data)
		except zlib.error:
			raise DecodeError(_(u'Invalid zlib/deflate data.'))
		return Codec.decode(data, charset)
