# -*- coding: utf-8 -*-
from __future__ import absolute_import

from httoop.codecs.codec import Codec


class HTTP(Codec):

	mimetype = 'message/http'

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):
		return bytes(data) + bytes(data.headers) + bytes(data.body)

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):
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
