# -*- coding: utf-8 -*-
from __future__ import absolute_import

from typing import Optional, Union

from httoop.codecs.codec import Codec


class HTTP(Codec):

	mimetype = 'message/http'

	@classmethod
	def encode(cls, data: Union["Request", "Response"], charset: Optional[str]=None, mimetype: Optional["ContentType"]=None) -> bytes:
		return bytes(data) + bytes(data.headers) + bytes(data.body)

	@classmethod
	def decode(cls, data: bytes, charset: Optional[str]=None, mimetype: Optional["ContentType"]=None) -> Union["Request", "Response"]:
		from httoop.messages import Request, Response
		line, data = data.split(b'\r\n', 1)
		message = Request()
		try:
			message.parse(line)
		except ValueError:
			message = Response()
			message.parse(line)
		headers, data = data.split(b'\r\n\r\n', 1)
		message.headers.parse(headers)
		message.body.parse(data)
		return message
