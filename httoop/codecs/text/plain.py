# -*- coding: utf-8 -*-
from typing import Optional

from httoop.codecs.codec import Codec
from httoop.exceptions import DecodeError, EncodeError


class PlainText(Codec):

	mimetype = 'text/plain'

	@classmethod
	def decode(cls, data: bytes, charset: Optional[str]=None, mimetype: Optional["ContentType"]=None) -> str:
		try:
			assert isinstance(data, bytes)
			return data.decode(charset or 'UTF-8')
		except UnicodeDecodeError:
			raise DecodeError(u'Wrong encoding.')

	@classmethod
	def encode(cls, data: str, charset: Optional[str]=None, mimetype: Optional["ContentType"]=None) -> bytes:
		try:
			assert not isinstance(data, bytes)
			return data.encode(charset or 'UTF-8')
		except UnicodeEncodeError:
			raise EncodeError(u'Wrong encoding.')
