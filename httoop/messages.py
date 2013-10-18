# -*- coding: utf-8 -*-
"""HTTP request and response messages

.. seealso:: :rfc:`2616#section-4`
"""

__all__ = ['Message', 'Request', 'Response', 'Protocol']

import re

from httoop.headers import Headers
from httoop.status import Status
from httoop.statuses import STATUSES
from httoop.body import Body
from httoop.uri import URI
from httoop.date import Date
from httoop.exceptions import InvalidLine, InvalidURI
from httoop.util import ByteString, text_type


class Protocol(tuple):
	u"""The HTTP protocol version"""

	def __str__(self):
		return 'HTTP/%d.%d' % self

	@property
	def name(self):
		return 'HTTP'

	@property
	def major(self):
		return self[0]

	@property
	def minor(self):
		return self[1]


class Method(text_type):
	u"""A HTTP request method"""

	safe_methods = (u'GET', u'HEAD', u'PUT', u'DELETE', u'OPTIONS', u'TRACE')

	idempotent_methods = (u'GET', u'HEAD')

	def __init__(self, method):
		# TODO: make sure the method is HTTP "token"
		if isinstance(method, text_type):
			method = method.encode('ascii').decode('ascii')
		elif isinstance(method, bytes):
			method = method.decode('ascii')

		super(Method, self).__init__(method)

		self.idempotent = self in self.safe_methods
		self.safe = self in self.idempotent_methods


class Message(ByteString):
	u"""A HTTP message

		.. seealso:: :rfc:`2616#section-4`
	"""

	VERSION_RE = re.compile(r"^HTTP/(\d+).(\d+)\Z")

	def __init__(self, protocol=None, headers=None, body=None):
		u"""Initiates a new Message to hold information about the message.

			:param protocol: the requested protocol
			:type  protocol: str

			:param headers: the request headers
			:type  headers: dict or :class:`Headers`

			:param body: the request body
			:type  body: any
		"""
		self.__protocol = Protocol(protocol or (1, 1))
		self.__headers = Headers(headers or {})
		self.__body = Body(body or b'')

	def parse(self, version):
		u"""parses the HTTP protocol version

			:param version: the version string
			:type  version: bytes
		"""
		match = self.VERSION_RE.match(version)
		if match is None:
			raise InvalidLine(u"Invalid HTTP version: %r" % version.decode('ISO8859-1'))

		self.protocol = (int(match.group(1)), int(match.group(2)))

	def prepare(self):
		pass

	@property
	def protocol(self):
		return self.__protocol

	@protocol.setter
	def protocol(self, protocol):
		if not isinstance(protocol, Protocol):
			protocol = Protocol(protocol)
		self.__protocol = protocol

	# alias
	version = protocol

	@property
	def headers(self):
		return self.__headers

	@headers.setter
	def headers(self, headers):
		if not isinstance(headers, Headers):
			headers = type(self.__headers)(headers)
		self.__headers = headers

	@property
	def body(self):
		return self.__body

	@body.setter
	def body(self, body):
		self.__body.set(body)

	def compose_message(self):
		u"""Compose the whole HTTP Message"""
		start_line = bytes(self)
		headers = bytes(self.headers)
		body = bytes(self.body)
		return b"%s%s%s" % (start_line, headers, body)

	def __repr__(self):
		return '<HTTP Message(protocol=%s)>' % (self.protocol,)


class Request(Message):
	u"""A HTTP request message

		.. seealso:: :rfc:`2616#section-5`
	"""

	METHOD_RE = re.compile(r"^[A-Z0-9$-_.]{1,20}\Z")

	def __init__(self, method=None, uri=None, protocol=None, headers=None, body=None):
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
		bits = line.split(None, 2)
		if len(bits) != 3:
			raise InvalidLine(line)

		# version
		super(Request, self).parse(bits[2])

		# method
		if None is self.METHOD_RE.match(bits[0]):
			raise InvalidLine(u"Invalid method: %r" % bits[0].decode('ISO8859-1'))
		self.method = bits[0]  # HTTP method is case sensitive

		# URI
		try:
			self.uri = bits[1]
		except InvalidURI as exc:
			raise InvalidLine(u"Invalid request URL: %r" % text_type(exc))

	def compose(self):
		u"""composes the request line"""
		return b"%s %s %s\r\n" % (bytes(self.__method), bytes(self.__uri), bytes(self.protocol))

	def prepare(self):
		pass  # TODO: chunked, Content-Length, close?

	@property
	def method(self):
		return self.__method

	@method.setter
	def method(self, method):
		self.__method = Method(method)

	@property
	def uri(self):
		return self.__uri

	@uri.setter
	def uri(self, uri):
		self.__uri.set(uri)

	def __bytes__(self):
		return self.compose()

	def __repr__(self):
		return "<HTTP Request(%s %s %s)>" % (bytes(self.__method), bytes(self.__uri.path), bytes(self.protocol))


class Response(Message):
	u"""A HTTP response message

		.. seealso:: :rfc:`2616#section-6`
	"""

	STATUS_RE = re.compile(r"^([1-5]\d{2})(?:\s+([\s\w]*))\Z")

	def __init__(self, status=None, protocol=None, headers=None, body=None):
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

		bits = line.split(None, 1)
		if len(bits) != 2:
			raise InvalidLine(line)

		# version
		super(Response, self).parse(bits[0])

		# status
		match = self.STATUS_RE.match(bits[1])
		if match is None:
			raise InvalidLine(u"Invalid status %r" % bits[1].decode('ISO8859-1'))

		self.status = (int(match.group(1)), match.group(2))

	def compose(self):
		u"""composes the response line"""
		return b"%s %s\r\n" % (bytes(self.protocol), bytes(self.status))

	def prepare(self):
		u"""prepares the response for being ready for transmitting"""

		status = self.status
		if status < 200 or status in (204, 205, 304):
			# 1XX, 204 NO_CONTENT, 205 RESET_CONTENT, 304 NOT_MODIFIED
			self.body = None

		self.chunked = self.chunked
		if not self.chunked:
			self.headers['Content-Length'] = bytes(len(self.body))

		self.headers['Date'] = bytes(Date())

		# remove header which should not occur along with this status
		if int(status) in STATUSES:
			for header in STATUSES[int(status)].header_to_remove:
				self.headers.pop(header, None)

		self.close = self.close

	@property
	def status(self):
		return self.__status

	@status.setter
	def status(self, status):
		self.__status.set(status)

	@property
	def chunked(self):
		return self.body.chunked or self.headers.get("Transfer-Encoding") == 'chunked'

	@chunked.setter
	def chunked(self, chunked):
		if chunked:
			self.headers['Transfer-Encoding'] = 'chunked'
			self.headers.pop('Content-Length', None)
		else:
			self.headers.pop('Transfer-Encoding', None)

	@property
	def close(self):
		# 413 Request Entity Too Large
		# RFC 2616 Section 10.4.14
		if self.status == 413:
			pass
		elif self.headers.get('Connection') == 'close':
			pass
		elif self.protocol < (1, 1):
			pass
		else:
			return False
		return True

	@close.setter
	def close(self, close):
		if close and self.protocol >= (1, 1):
			self.headers['Connection'] = 'close'
		if not close and self.protocol < (1, 1):
			self.headers['Connection'] = 'keep-alive'

	def __bytes__(self):
		return self.compose()

	def __repr__(self):
		# TODO: do we really want to check the body length here?
		content_type = self.headers.get("Content-Type", "")
		return "<HTTP Response(%d %s (%d))>" % (self.status, content_type, len(self.body))
