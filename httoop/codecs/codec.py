# -*- coding: utf-8 -*-

from httoop.util import Unicode


class Codec(object):

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):  # pragma: no cover
		if isinstance(data, bytes):
			data = data.decode(charset or 'ascii')
		return data

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):  # pragma: no cover
		if isinstance(data, Unicode):
			data = data.encode(charset or 'ascii')
		return data

	@classmethod
	def iterencode(cls, data, charset=None, mimetype=None):  # pragma: no cover
		for part in data:
			yield cls.encode(part, charset, mimetype)

	@classmethod
	def iterdecode(cls, data, charset=None, mimetype=None):  # pragma: no cover
		for part in data:
			yield cls.decode(part, charset, mimetype)
