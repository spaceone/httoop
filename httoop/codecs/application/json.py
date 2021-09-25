# -*- coding: utf-8 -*-
from __future__ import absolute_import

from json import dumps as json_encode, loads as json_decode

from httoop.codecs.codec import Codec


class JSON(Codec):
	mimetype = 'application/json'

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):
		data = json_encode(data)
		if not isinstance(data, bytes):  # python3
			data = data.encode(charset or 'UTF-8')
		return data

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):
		return json_decode(data.decode(charset or 'ASCII'))
