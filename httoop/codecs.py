# -*- coding: utf-8 -*-
u"""Module containing various codecs which are
	common used in combination with HTTP
"""

__all__ = ['codecs', 'Codec', 'FormURLEncoded', 'MultipartFormData',
	'MultipartMixed', 'JSON', 'HTML', 'XML', 'PlainText']

from httoop.util import text_type, partial


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


class FormURLEncoded(Codec):
	mimetype = 'application/x-www-form-urlencoded'

	from httoop.util import parse_qsl
	decode = partial(parse_qsl, keep_blank_values=True, strict_parsing=True)

	from httoop.util import urlencode
	encode = partial(urlencode)


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


class PlainText(Codec):
	# TODO: is there a enconv lib in python?
	mimetype = 'text/plain'

	@classmethod
	def encode(cls, data):
		if isinstance(data, text_type):
			return data
		return data.encode('UTF-8')

	@classmethod
	def decode(cls, data):
		try:
			return data.decode('UTF-8')
		except UnicodeDecodeError:
			return data.decode('ISO8859-1')


class XML(Codec):
	mimetype = 'application/xml'


class HTML(Codec):
	mimetype = 'text/html'


codecs = dict((cls.mimetype, cls) for cls in locals().copy().values() if cls is not Codec and isinstance(cls, type) and issubclass(cls, Codec))
