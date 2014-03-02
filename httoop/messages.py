# -*- coding: utf-8 -*-
"""HTTP request and response messages

.. seealso:: :rfc:`2616#section-4`
"""

__all__ = ['Message', 'Request', 'Response', 'Protocol']

import re

from httoop.header import Headers
from httoop.status import Status
from httoop.body import Body
from httoop.uri import URI
from httoop.exceptions import InvalidLine
from httoop.util import Unicode
from httoop.meta import HTTPSemantic


class Protocol(object):
	u"""The HTTP protocol version"""
	__metaclass__ = HTTPSemantic
	__slots__ = ('name', '__protocol')

	@property
	def version(self):
		return tuple(self)

	@property
	def major(self):
		return self[0]

	@property
	def minor(self):
		return self[1]

	PROTOCOL_RE = re.compile(r"^(HTTP)/(\d+).(\d+)\Z")

	def __init__(self, protocol=(1, 1)):
		self.__protocol = protocol
		self.name = b'HTTP'
		self.set(protocol)

	def set(self, protocol):
		if isinstance(protocol, (bytes, Unicode)):
			protocol = self.parse(protocol)
		else:
			self.__protocol = tuple(protocol)

	def parse(self, protocol):
		match = self.PROTOCOL_RE.match(protocol)
		if match is None:
			raise InvalidLine(u"Invalid HTTP protocol: %r" % protocol.decode('ISO8859-1'))
		self.__protocol = (int(match.group(2)), int(match.group(3)))
		self.name = match.group(1)

	def compose(self):
		return b'%s/%d.%d' % (self.name, self.major, self.minor)

	def __iter__(self):
		return self.__protocol.__iter__()

	def __getitem__(self, key):
		return self.version[key]

	def __cmp__(self, other):
		if isinstance(other, (bytes, Unicode)):
			return super(Protocol, self).__cmp__(other)
		return cmp(self.__protocol, other)


class Method(object):
	u"""A HTTP request method"""
	__metaclass__ = HTTPSemantic
	__slots__ = ('__method')

	@property
	def safe(self):
		return self in self.safe_methods

	@property
	def idempotent(self):
		return self in self.idempotent_methods

	safe_methods = (u'GET', u'HEAD')
	idempotent_methods = (u'GET', u'HEAD', u'PUT', u'DELETE', u'OPTIONS', u'TRACE')
	METHOD_RE = re.compile(r"^[A-Z0-9$-_.]{1,20}\Z", re.IGNORECASE)

	def __init__(self, method=None):
		self.set(method or u'GET')

	def set(self, method):
		if isinstance(method, Unicode):
			method = method.encode('ASCII')
		self.parse(method)

	def parse(self, method):
		if not self.METHOD_RE.match(method):
			raise InvalidLine(u"Invalid method: %r" % method.decode('ISO8859-1'))
		self.__method = method

	def compose(self):
		return self.__method


class Message(object):
	u"""A HTTP message

		.. seealso:: :rfc:`2616#section-4`
	"""
	__metaclass__ = HTTPSemantic
	__slots__ = ('__protocol', '__headers', '__body')

	@property
	def protocol(self):
		return self.__protocol

	@protocol.setter
	def protocol(self, protocol):
		self.__protocol.set(protocol)

	@property
	def headers(self):
		return self.__headers

	@headers.setter
	def headers(self, headers):
		self.__headers.set(headers)

	@property
	def body(self):
		return self.__body

	@body.setter
	def body(self, body):
		self.__body.set(body)

	@property
	def trailer(self):
		return Headers((key, self.headers[key]) for key in self.headers.values('Trailer') if key in self.message.headers)

#	@trailer.setter
#	def trailer(self, trailer):
#		self.headers.pop('Trailer', None)
#		if trailer:
#			trailer = Headers(trailer)
#			for key in trailer:
#				self.headers.append('Trailer', key)
#			self.headers.elements('Trailer')  # sanitize
#			self.headers.merge(trailer)

	def __init__(self, protocol=None, headers=None, body=None):
		u"""Initiates a new Message to hold information about the message.

			:param protocol: the requested protocol
			:type  protocol: str|tuple

			:param headers: the request headers
			:type  headers: dict or :class:`Headers`

			:param body: the request body
			:type  body: any
		"""
		self.__protocol = Protocol(protocol or (1, 1))
		self.__headers = Headers(headers or {})
		self.__body = Body(body or b'')

	def parse(self, protocol):
		u"""parses the HTTP protocol version

			:param protocol: the protocol version string
			:type  protocol: bytes
		"""

		self.protocol.parse(protocol)

	def __repr__(self):
		return '<HTTP Message(protocol=%s)>' % (self.protocol,)


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

	def __init__(self, method=None, uri=None, headers=None, body=None, protocol=None):
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
			raise InvalidLine(line.decode('ISO8859-1'))

		# protocol version
		super(Request, self).parse(version)

		# method
		self.method.parse(method)

		# URI
		self.uri.parse(uri)
		self.uri.validate_http_request_uri()  # TODO: move the method into here

	def compose(self):
		u"""composes the request line"""
		return b"%s %s %s\r\n" % (bytes(self.__method), bytes(self.__uri), bytes(self.protocol))

	def __repr__(self):
		return "<HTTP Request(%s %s %s)>" % (bytes(self.__method), bytes(self.__uri.path), bytes(self.protocol))


class Response(Message):
	u"""A HTTP response message

		.. seealso:: :rfc:`2616#section-6`
	"""
	__slots__ = ('__protocol', '__headers', '__body', '__status')

	@property
	def status(self):
		return self.__status

	@status.setter
	def status(self, status):
		self.__status.set(status)

	def __init__(self, status=None, headers=None, body=None, protocol=None):
		"""Creates a new Response object to hold information about the response.

			:param status:
				A HTTP status, default is 200
			:type status:
				int or str or :class:`Status`
		"""

		super(Response, self).__init__(protocol, headers, body)

		self.__status = Status(status or 200)

	def parse(self, line):
		u"""parses the response line"""

		bits = line.strip().split(None, 1)
		try:
			version, status = bits
		except ValueError:
			raise InvalidLine(line.decode('ISO8859-1'))

		# version
		super(Response, self).parse(version)

		# status
		self.status.parse(status)

	def compose(self):
		u"""composes the response line"""
		return b"%s %s\r\n" % (bytes(self.protocol), bytes(self.status))

	def __repr__(self):
		return "<HTTP Response(%d %s)>" % (self.status, self.body.mimetype)
