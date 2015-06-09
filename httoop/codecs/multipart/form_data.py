# -*- coding: utf-8 -*-
from httoop.codecs.common import Codec
from httoop.exceptions import DecodeError

__name__ = 'form-data'


class MultipartFormData(Codec):
	mimetype = 'multipart/form-data'

	@classmethod
	def encode(self, data, charset=None, mimetype=None):
		boundary = mimetype.boundary.encode('ISO8859-1')
		multipart = b''
		for body in data:
			multipart += b'--%s\r\n%s%s\r\n' % (boundary, body.headers, body)
		multipart += b'--%s--\r\n' % (boundary,)
		return multipart

	@classmethod
	def decode(self, data, charset=None, mimetype=None):
		boundary = mimetype.boundary.encode('ISO8859-1')
		parts = data.split(b'--%s' % (boundary,))
		part = parts.pop(0)
		if part:
			raise DecodeError(u'Data before boundary: %r' % (part.decode('ISO8859-1'),))
		try:
			part = parts.pop()
		except IndexError:
			raise DecodeError(u'No end of boundary')
		if part not in (b'--', b'--\r\n'):
			raise DecodeError(u'Invalid multipart end: %r' % (part.decode('ISO8859-1')))

		from httoop.messages.body import Body
		multiparts = []
		for part in parts:
			if not part.startswith('\r\n'):
				raise DecodeError(u'Invalid boundary end: %r' % (part[:2].decode('ISO8859-1')))
			part = part[2:]
			headers, separator, content = part.partition(b'\r\n\r\n')
			if not separator:
				raise DecodeError(u'Multipart does not contain CRLF header separator')
			if not content.endswith('\r\n'):
				raise DecodeError(u'Multipart does not end with CRLF: %r' % (content[-2].decode('ISO8859-1')))
			content = content[:-2]
			body = Body()
			body.headers.parse(headers)
			body.parse(content)
			multiparts.append(body)
		return multiparts
