# -*- coding: utf-8 -*-

from httoop.util import Unicode


class Codec(object):
	@classmethod
	def decode(cls, data, charset=None, mimetype=None):  # pragma: no cover
		raise NotImplementedError

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):  # pragma: no cover
		raise NotImplementedError

	@classmethod
	def iterencode(cls, data, charset=None, mimetype=None):  # pragma: no cover
		raise NotImplementedError

	@classmethod
	def iterdecode(cls, data, charset=None, mimetype=None):  # pragma: no cover
		raise NotImplementedError


class Enconv(Codec):
	mimetype = None

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):
		if isinstance(data, Unicode):
			return data
		for encoding in (charset or 'UTF-8', 'UTF-8', 'ISO8859-1'):
			try:
				return data.decode(encoding)
			except UnicodeDecodeError:
				pass

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):
		charset = charset or 'UTF-8'
		if isinstance(data, bytes):
			try:
				return data.decode('UTF-8').encode(charset)
			except UnicodeDecodeError:
				return data.decode('ISO8859-1').encode(charset)
		return data.encode(charset)
