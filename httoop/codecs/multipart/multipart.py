# -*- coding: utf-8 -*-

from httoop.codecs.codec import Codec
from httoop.exceptions import DecodeError
from httoop.util import _


class Multipart(Codec):

	mimetype = 'multipart/*'
	default_content_type = 'text/plain; charset=US-ASCII'

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):
		boundary = mimetype.boundary.encode('ISO8859-1')
		multipart = b''
		for body in data:
			multipart += b'--%s\r\n%s%s\r\n' % (boundary, body.headers, body)
		multipart += b'--%s--\r\n' % (boundary,)
		return multipart

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):
		boundary = mimetype.boundary.encode('ISO8859-1')
		parts = data.split(b'--%s' % (boundary,))
		part = parts.pop(0)
		if part:
			raise DecodeError(_(u'Data before boundary: %r'), part.decode('ISO8859-1'))
		part = parts.pop()
		if part not in (b'--', b'--\r\n'):
			raise DecodeError(_(u'Invalid multipart end: %r'), part.decode('ISO8859-1'))

		from httoop.messages.body import Body
		multiparts = []
		for part in parts:
			if not part.startswith(b'\r\n'):
				raise DecodeError(_(u'Invalid boundary end: %r'), part[:2].decode('ISO8859-1'))
			part = part[2:]
			headers, separator, content = part.partition(b'\r\n\r\n')
			if not separator:
				raise DecodeError(_(u'Multipart does not contain CRLF header separator'))
			if not content.endswith(b'\r\n'):
				raise DecodeError(_(u'Multipart does not end with CRLF: %r'), content[-2:].decode('ISO8859-1'))
			content = content[:-2]
			body = Body()
			body.headers.clear()
			body.headers.parse(headers)
			body.headers.setdefault('Content-Type', cls.default_content_type)
			body.parse(content)
			multiparts.append(body)
		return multiparts
