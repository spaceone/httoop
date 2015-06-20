# -*- coding: utf-8 -*-


class Percent(object):
	u"""Percentage encoding

		>>> Percent.encode(u"!#$&'()*+,/:;=?@[]")
		'%21%23%24%26%27%28%29%2A%2B%2C%2F%3A%3B%3D%3F%40%5B%5D'
		>>> Percent.decode('%21%23%24%26%27%28%29%2a%2b%2c%2f%3a%3b%3d%3f%40%5b%5d')
		u"!#$&'()*+,/:;=?@[]"
	"""

	GEN_DELIMS = b":/?#[]@"
	SUB_DELIMS = b"!$&'()*+,;="

	RESERVED_CHARS = GEN_DELIMS + SUB_DELIMS + b'%'

	HEX_MAP = dict((a + b, chr(int(a + b, 16))) for a in '0123456789ABCDEFabcdef' for b in '0123456789ABCDEFabcdef')

	@classmethod
	def decode(cls, data, charset=None):
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
	def encode(cls, data, charset=None):
		data = data.encode(charset or 'ISO8859-1')
		if not any(d in data for d in cls.RESERVED_CHARS):
			return data
		return b''.join(b'%%%s' % (d.encode('hex').upper()) if d in cls.RESERVED_CHARS else d for d in data)
