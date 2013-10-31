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
	def decode(cls, data):
		raise NotImplemented

	@classmethod
	def encode(cls, data):
		raise NotImplemented

	@classmethod
	def iterencode(cls, data):
		raise NotImplemented

	@classmethod
	def iterdecode(cls, data):
		raise NotImplemented


class Enconv(Codec):
	mimetype = None

	@classmethod
	def decode(cls, data):
		# TODO: if the data is already bytes we can also try to .decode(guess).encode('UTF-8').decode('UTF-8')
		try:
			return data.decode('UTF-8')
		except UnicodeDecodeError:
			return data.decode('ISO8859-1')

	@classmethod
	def encode(cls, data):
		if isinstance(data, Unicode):
			return data
		return data.encode('UTF-8')


class Percent(Codec):
	u"""Percentage encoding

		>>> Percent.encode(u"!#$&'()*+,/:;=?@[]")
		'%21%23%24%26%27%28%29%2a%2b%2c%2f%3a%3b%3d%3f%40%5b%5d'
		>>> Percent.decode('%21%23%24%26%27%28%29%2a%2b%2c%2f%3a%3b%3d%3f%40%5b%5d')
		u"!#$&'()*+,/:;=?@[]"
	"""
	mimetype = None

	GEN_DELIMS = b":/?#[]@"
	SUB_DELIMS = b"!$&'()*+,;="

	RESERVED_CHARS = GEN_DELIMS + SUB_DELIMS + b'%'

	HEX_MAP = dict((a+b, chr(int(a+b, 16))) for a in '0123456789ABCDEFabcdef' for b in '0123456789ABCDEFabcdef')

	@classmethod
	def decode(cls, data):
		if '%' not in data:
			return Enconv.decode(data)
		def _decode(data):
			data = data.split(b'%')
			yield data.pop(0)
			for item in data:
				try:
					yield cls.HEX_MAP[item[:2]]
					yield item[2:]
				except KeyError:
					yield b'%'
					yield item
		return Enconv.decode(b''.join(_decode(data)))

	@classmethod
	def encode(cls, data):
		data = Enconv.encode(data)
		if not any(d in data for d in cls.RESERVED_CHARS):
			return data
		return b''.join('%%%s' % (hex(ord(d))[2:]) if d in cls.RESERVED_CHARS else d for d in data)


class FormURLEncoded(Codec):
	mimetype = 'application/x-www-form-urlencoded'

	unquote = Percent.decode
	quote = Percent.encode

	@classmethod
	def decode(cls, data):
		fields = (field.split(b'=', 1) + [b''] for field in data.split(b'&'))
		fields = ((field[0], field[1]) for field in fields)
		return tuple((cls.unquote(name), cls.unquote(value)) for name, value in fields)

	@classmethod
	def encode(cls, data):
		return b'&'.join(b'%s=%s' % (cls.quote(name), cls.quote(value)) for name, value in data if name and value)


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
	def encode(cls, data):
		return cls.json_encode(data)

	@classmethod
	def decode(cls, data):
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
