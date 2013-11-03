# -*- coding: utf-8 -*-
u"""Module containing various codecs which are
	common used in combination with HTTP
"""

__all__ = ['CODECS', 'Codec', 'FormURLEncoded', 'MultipartFormData',
	'MultipartMixed', 'JSON', 'HTML', 'XML', 'PlainText']

from httoop.util import Unicode

CODECS = dict()


class Codec(object):
	@classmethod
	def decode(cls, data, charset=None):
		raise NotImplemented

	@classmethod
	def encode(cls, data, charset=None):
		raise NotImplemented

	@classmethod
	def iterencode(cls, data, charset=None):
		raise NotImplemented

	@classmethod
	def iterdecode(cls, data, charset=None):
		raise NotImplemented


class Enconv(Codec):
	mimetype = None

	@classmethod
	def decode(cls, data, charset=None):
		if isinstance(data, Unicode):
			return data
		for encoding in (charset or 'UTF-8', 'UTF-8', 'ISO8859-1'):
			try:
				return data.decode(encoding)
			except UnicodeDecodeError:
				pass

	@classmethod
	def encode(cls, data, charset=None):
		charset = charset or 'UTF-8'
		if isinstance(data, bytes):
			try:
				return data.decode('UTF-8').encode(charset)
			except UnicodeDecodeError:
				return data.decode('ISO8859-1').encode(charset)
		return data.encode(charset)


class Percent(Codec):
	u"""Percentage encoding

		>>> Percent.encode(u"!#$&'()*+,/:;=?@[]")
		'%21%23%24%26%27%28%29%2A%2B%2C%2F%3A%3B%3D%3F%40%5B%5D'
		>>> Percent.decode('%21%23%24%26%27%28%29%2a%2b%2c%2f%3a%3b%3d%3f%40%5b%5d')
		u"!#$&'()*+,/:;=?@[]"
	"""
	mimetype = None

	GEN_DELIMS = b":/?#[]@"
	SUB_DELIMS = b"!$&'()*+,;="

	RESERVED_CHARS = GEN_DELIMS + SUB_DELIMS + b'%'

	HEX_MAP = dict((a + b, chr(int(a + b, 16))) for a in '0123456789ABCDEFabcdef' for b in '0123456789ABCDEFabcdef')

	@classmethod
	def decode(cls, data, charset=None):
		return Enconv.decode(b''.join(cls._decode_iter(data)), charset)

	@classmethod
	def _decode_iter(cls, data):
		if b'%' not in data:
			yield data
			return
		data = data.split(b'%')
		yield data.pop(0)
		for item in data:
			try:
				yield cls.HEX_MAP[item[:2]]
				yield item[2:]
			except KeyError:
				yield b'%'
				yield item

	@classmethod
	def encode(cls, data, charset=None):
		data = Enconv.encode(data, charset)
		if not any(d in data for d in cls.RESERVED_CHARS):
			return data
		return b''.join('%%%s' % (hex(ord(d))[2:].upper()) if d in cls.RESERVED_CHARS else d for d in data)


class FormURLEncoded(Codec):
	mimetype = 'application/x-www-form-urlencoded'

	unquote = Percent.decode
	quote = Percent.encode

	@classmethod
	def decode(cls, data, charset=None):
		if not data:
			return ()
		fields = (field.partition(b'=')[::2] for field in data.split(b'&'))
		return tuple((cls.unquote(name, charset), cls.unquote(value, charset)) for name, value in fields)

	@classmethod
	def encode(cls, data, charset=None):
		return b'&'.join(b'%s=%s' % (cls.quote(name, charset), cls.quote(value, charset)) for name, value in data if name and value)


class MultipartFormData(Codec):
	mimetype = 'multipart/form-data'


class MultipartMixed(Codec):
	mimetype = 'multipart/mixed'


class JSON(Codec):
	mimetype = 'application/json'
	# TODO: http://stackoverflow.com/questions/712791/what-are-the-differences-between-json-and-simplejson-python-modules#answer-16131316
	try:
		from simplejson import dumps as json_encode
		from simplejson import loads as json_decode
	except ImportError:
		from json import dumps as json_encode
		from json import loads as json_decode

	@classmethod
	def encode(cls, data, charset=None):
		return cls.json_encode(data)

	@classmethod
	def decode(cls, data, charset=None):
		return cls.json_decode(data)


class PlainText(Enconv):
	mimetype = 'text/plain'


class XML(Codec):
	mimetype = 'application/xml'


class HTML(Codec):
	mimetype = 'text/html'


for cls in locals().copy().values():
	if cls is not Codec and isinstance(cls, type) and issubclass(cls, Codec):
		CODECS[cls.mimetype] = cls
