# -*- coding: utf-8 -*-
"""HTTP request and response messages

.. seealso:: :rfc:`2616#section-4`
"""

from httoop.exceptions import InvalidLine, InvalidURI
from httoop.messages.message import Message
from httoop.messages.method import Method
from httoop.uri import HTTP as URI
from httoop.util import _

__all__ = ('Request',)


class Request(Message):
	u"""A HTTP request message

		.. seealso:: :rfc:`2616#section-5`
	"""
	__slots__ = ('__protocol', '__headers', '__body', '__uri', '__method')

	@property
	def method(self):
		return self.__method

	@method.setter
	def method(self, method):
		self.__method.set(method)

	@property
	def uri(self):
		return self.__uri

	@uri.setter
	def uri(self, uri):
		self.__uri.set(uri)

	def __init__(self, method=None, uri=None, headers=None, body=None, protocol=None):  # pylint: disable=R0913
		"""Creates a new Request object to hold information about a request.

			:param method: the requested method
			:type  method: str

			:param uri: the requested URI
			:type  uri: str or :class:`URI`

		"""

		super(Request, self).__init__(protocol, headers, body)
		self.__method = Method(method or 'GET')
		self.__uri = URI(uri or '/')

	def parse(self, line):
		"""parses the request line and sets method, uri and protocol version
			:param line: the request line
			:type  line: bytes
		"""
		bits = line.strip().split(None, 2)
		try:
			method, uri, version = bits
		except ValueError:
			raise InvalidLine(_(u'Invalid request line: %r'), line.decode('ISO8859-1'))

		# protocol version
		super(Request, self).parse(version)

		# method
		self.method.parse(method)

		# URI
		if uri.startswith(b'//'):
			raise InvalidURI(_(u'The request URI must be an absolute path or contain a scheme.'))
		if self.method == u'CONNECT':
			uri = b'//%s' % (uri,)
		self.uri.parse(uri)
		self.validate_request_uri()

	def validate_request_uri(self):
		uri = self.uri
		if not isinstance(uri, (uri.SCHEMES[b'http'], uri.SCHEMES[b'https'])):
			raise InvalidURI(_(u'The request URI scheme must be HTTP based.'))
		if uri.fragment or uri.username or uri.password:
			raise InvalidURI(_(u'The request URI must not contain fragments or user information.'))
		if uri.path.startswith(u'//'):
			raise InvalidURI(_(u'The request URI path must not start with //.'))
		if uri.path and uri.path != u'*' and uri.path[0] != u'/':
			raise InvalidURI(_(u'The request URI path must start with /.'))
		if self.method == u'CONNECT' and (uri.scheme or uri.path or uri.query_string or not uri.host):
			raise InvalidURI(_(u'The request URI of an CONNECT request must be a authority.'))

	def compose(self):
		u"""composes the request line"""
		self.validate_request_uri()
		return b"%s %s %s\r\n" % (bytes(self.__method), bytes(self.__uri) or b'/', bytes(self.protocol))

	def __repr__(self):
		return "<HTTP Request(%s %s %s)>" % (self.__method, self.__uri.path, self.protocol)
