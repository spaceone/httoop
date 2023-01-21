# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional

from httoop.util import Unicode


class Codec(object):

	@classmethod
	def decode(cls, data: bytes, charset: Optional[str]=None, mimetype: None=None) -> str:  # pragma: no cover
		if isinstance(data, bytes):
			data = data.decode(charset or 'ascii')
		return data

	@classmethod
	def encode(cls, data: bytes, charset: None=None, mimetype: None=None) -> bytes:  # pragma: no cover
		if isinstance(data, Unicode):
			data = data.encode(charset or 'ascii')
		return data

	@classmethod
	def iterencode(cls, data: Dict[Any, Any], charset: Optional[str]=None, mimetype: Optional["ContentType"]=None) -> None:  # pragma: no cover
		for part in data:
			yield cls.encode(part, charset, mimetype)

	@classmethod
	def iterdecode(cls, data, charset=None, mimetype=None):  # pragma: no cover
		for part in data:
			yield cls.decode(part, charset, mimetype)
