# -*- coding: utf-8 -*-

from httoop import six


class Percent(object):
	u"""Percentage encoding

		>>> Percent.quote(b"!#$&'()*+,/:;=?@[]")
		b'%21%23%24%26%27%28%29%2A%2B%2C%2F%3A%3B%3D%3F%40%5B%5D'
		>>> Percent.unquote(b'%21%23%24%26%27%28%29%2a%2b%2c%2f%3a%3b%3d%3f%40%5b%5d')
		b"!#$&'()*+,/:;=?@[]"
	"""

	HEX_MAP = dict(((a + b).encode('ASCII'), six.int2byte(int(a + b, 16))) for a in '0123456789ABCDEFabcdef' for b in '0123456789ABCDEFabcdef')

	# ABNF
	GEN_DELIMS = b":/?#[]@"
	SUB_DELIMS = b"!$&'()*+,;="

	RESERVED = GEN_DELIMS + SUB_DELIMS + b'%'
	ALPHA = b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	DIGIT = b'0123456789'
	UNRESERVED = ALPHA + DIGIT + b'-._~'

	SCHEME = ALPHA + DIGIT + b'+-.'
	PCHAR = UNRESERVED + SUB_DELIMS + b':@'
	USERINFO = UNRESERVED + SUB_DELIMS + b':'
	PATH = PCHAR + b'/'
	QUERY = PCHAR + b'/?'
	FRAGMENT = PCHAR + b'/?'

	@classmethod
	def unquote(cls, data):
		return b''.join(cls._decode_iter(data))

	@classmethod
	def _decode_iter(cls, data):
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
	def quote(cls, data, charset=UNRESERVED):
		charset = {six.int2byte(c) for c in six.iterbytes(charset)} - {b'%'}
		data = (six.int2byte(d) for d in six.iterbytes(data))
		return b''.join(b'%%%X' % (ord(d), ) if d not in charset else d for d in data)
