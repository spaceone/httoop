# -*- coding: utf-8 -*-
from __future__ import absolute_import

from json import dumps as json_encode, loads as json_decode
from typing import Any, Dict, Optional, Union

from httoop.codecs.codec import Codec


class JSON(Codec):
	mimetype = 'application/json'

	@classmethod
	def encode(cls, data: Union[Dict[str, str], "Resource"], charset: Optional[str]=None, mimetype: Optional["ContentType"]=None) -> bytes:
		data = json_encode(data)
		if not isinstance(data, bytes):  # python3
			data = data.encode(charset or 'UTF-8')
		return data

	@classmethod
	def decode(cls, data: bytes, charset: Optional[str]=None, mimetype: Optional["ContentType"]=None) -> Dict[str, Any]:
		return json_decode(data.decode(charset or 'ASCII'))
