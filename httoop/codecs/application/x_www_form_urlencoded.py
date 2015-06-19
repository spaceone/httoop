# -*- coding: utf-8 -*-
from httoop.codecs.common import Codec, Enconv
from httoop.exceptions import DecodeError
from httoop.util import Unicode


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
	def decode(cls, data, charset=None, mimetype=None):
		return b''.join(cls._decode_iter(data)).decode(charset or 'ISO8859-1')

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
	def encode(cls, data, charset=None, mimetype=None):
		data = Enconv.encode(data, charset)
		if not any(d in data for d in cls.RESERVED_CHARS):
			return data
		return b''.join(b'%%%s' % (d.encode('hex').upper()) if d in cls.RESERVED_CHARS else d for d in data)


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


class QueryString(FormURLEncoded):
	INVALID = set(map(chr, list(range(32)) + [127]))
#	INVALID_HEX = [Percent.decode(i) for i in INVALID]
#	INVALID_RE = re.compile('(?:{})'.format((u'|'.join(INVALID_HEX)).encode('ascii')))

	@classmethod
	def quote(cls, data, charset):
		return super(QueryString, cls).quote(data, charset).replace(b' ', b'+')

	@classmethod
	def unquote(cls, data, charset):
		data = Enconv.decode(data, charset)
		return super(QueryString, cls).unquote(data.replace(b'+', b' '), charset)

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):
		if set(Percent.decode(data)) & cls.INVALID:
			raise DecodeError('Invalid query string: contains invalid token')

		return super(QueryString, cls).decode(data, charset)

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):
		data = super(QueryString, cls).encode(data, charset)

# TODO: decide to remove invalid chars or strip them out
# FIXME: broken?
#		if set(Percent.encode(data)) & cls.INVALID:
#			raise DecodeError('Invalid query string: contains invalid token')

		# strip out illegal chars
		for invalid in cls.INVALID:
			data = data.replace(Percent.decode(invalid.encode('ascii')), u'')
		# data = cls.INVALID_RE.sub(data, u'')

		return data
