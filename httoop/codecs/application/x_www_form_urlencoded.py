# -*- coding: utf-8 -*-
from httoop.codecs.codec import Codec
from httoop.uri.percent_encoding import Percent
#from httoop.util import Unicode


class FormURLEncoded(Codec):
	mimetype = 'application/x-www-form-urlencoded'

	UNQUOTED = Percent.UNRESERVED

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):
		if not data:
			return ()
		data = data.replace(b'+', b' ').strip(b'&').split(b'&')
		fields = (field.partition(b'=')[::2] for field in data if field)
		return tuple((cls.unquote(name, charset), cls.unquote(value, charset)) for name, value in fields)

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):
		#if isinstance(data, (Unicode, bytes)):
		#	data = cls.decode(data, charset)
		if isinstance(data, dict):
			data = data.items()
		data = ((cls.quote(name, charset), cls.quote(value, charset)) for name, value in tuple(data))
		data = b'&'.join(b'%s=%s' % (name, value) if (name and value) else b'%s%s' % (name, value) for name, value in data)
		return data.replace(b'%20', b'+')

	@classmethod
	def unquote(cls, data, charset=None):
		return Percent.unquote(data).decode(charset or 'ISO8859-1')

	@classmethod
	def quote(cls, data, charset=None):
		data = data.encode(charset or 'ISO8859-1')
		return Percent.quote(data, cls.UNQUOTED)
