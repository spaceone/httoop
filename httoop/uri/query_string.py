# -*- coding: utf-8 -*-
import stringprep

from httoop.codecs.application.x_www_form_urlencoded import FormURLEncoded
from httoop.exceptions import InvalidURI as DecodeError
from httoop.uri.percent_encoding import Percent
from httoop.util import _


class QueryString(FormURLEncoded):
	INVALID = (stringprep.in_table_c21,)

	@classmethod
	def quote(cls, data, charset=None):
		data = data.encode(charset or 'ISO8859-1')
		return Percent.quote(data, Percent.QUERY.replace(b'+', b''))

	@classmethod
	def decode(cls, data, charset=None):
		if any(in_table(x) for x in cls.unquote(data.encode('ISO8859-1'), 'ISO8859-1') for in_table in cls.INVALID):
			raise DecodeError(_(u'Invalid query string: contains invalid token'))
		data = super(QueryString, cls).decode(data, charset)
		return data
