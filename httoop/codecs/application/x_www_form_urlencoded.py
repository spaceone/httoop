# -*- coding: utf-8 -*-
from httoop.codecs.common import Codec
from httoop.exceptions import DecodeError
from httoop._percent import Percent
from httoop.util import Unicode


class FormURLEncoded(Codec):
	mimetype = 'application/x-www-form-urlencoded'

	unquote = Percent.decode
	quote = Percent.encode

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):
		if not data:
			return ()
		fields = (field.partition(b'=')[::2] for field in data.split(b'&'))
		return tuple((cls.unquote(name, charset), cls.unquote(value, charset)) for name, value in fields)

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):
		if isinstance(data, (Unicode, bytes)):
			data = cls.decode(data, charset)
		elif isinstance(data, dict):
			data = data.items()
		return b'&'.join(b'%s=%s' % (cls.quote(name, charset), cls.quote(value, charset)) for name, value in tuple(data) if name and value)
