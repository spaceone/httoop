# -*- coding: utf-8 -*-
from httoop.codecs.application.x_www_form_urlencoded import FormURLEncoded
from httoop.exceptions import DecodeError
from httoop._percent import Percent


class QueryString(FormURLEncoded):
	INVALID = set(map(chr, list(range(32)) + [127]))
#	INVALID_HEX = [Percent.decode(i) for i in INVALID]
#	INVALID_RE = re.compile('(?:{})'.format((u'|'.join(INVALID_HEX)).encode('ascii')))

	@classmethod
	def quote(cls, data, charset):
		return super(QueryString, cls).quote(data, charset).replace(b' ', b'+')

	@classmethod
	def unquote(cls, data, charset):
		data = data.decode(charset or 'ISO8859-1')
		return super(QueryString, cls).unquote(data.replace(b'+', b' '), charset)

	@classmethod
	def decode(cls, data, charset=None):
		if set(Percent.decode(data)) & cls.INVALID:
			raise DecodeError('Invalid query string: contains invalid token')

		return super(QueryString, cls).decode(data, charset)

	@classmethod
	def encode(cls, data, charset=None):
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
