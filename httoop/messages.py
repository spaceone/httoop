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
from httoop.util import ByteString, Unicode


class Protocol(ByteString):
	u"""The HTTP protocol version"""

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

	def __bytes__(self):
		return b'%s/%d.%d' % (self.name, self.major, self.minor)

	def __iter__(self):
		return self.__protocol.__iter__()

	def __getitem__(self, key):
		return self.version[key]

	def __cmp__(self, other):
		if isinstance(other, (bytes, Unicode)):
			return super(Protocol, self).__cmp__(other)
		return cmp(self.__protocol, other)


class Method(ByteString):
	u"""A HTTP request method"""

	@property
	def safe(self):
		return self in self.safe_methods

	@property
	def idempotent(self):
		return self in self.idempotent_methods

	safe_methods = (u'GET', u'HEAD', u'PUT', u'DELETE', u'OPTIONS', u'TRACE')

	idempotent_methods = (u'GET', u'HEAD')

	METHOD_RE = re.compile(r"^[A-Z0-9$-_.]{1,20}\Z", re.IGNORECASE)

	def __init__(self, method):
		self.set(method)

	def set(self, method):
		if isinstance(method, Unicode):
			method = method.encode('ascii')
		self.parse(method)

	def parse(self, method):
		if not self.METHOD_RE.match(method):
			raise InvalidLine(u"Invalid method: %r" % method.decode('ISO8859-1'))
		self.__method = method

	def __bytes__(self):
		return self.__method


class Message(ByteString):
	u"""A HTTP message

		.. seealso:: :rfc:`2616#section-4`
	"""

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

	def parse(self, protocol):
		u"""parses the HTTP protocol version

			:param protocol: the protocol version string
			:type  protocol: bytes
		"""

		self.protocol.parse(protocol)

	def prepare(self):
		pass

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

	def compose_message(self):
		u"""Compose the whole HTTP Message"""
		start_line = bytes(self)
		headers = bytes(self.headers)
		body = bytes(self.body)
		return b"%s%s%s" % (start_line, headers, body)

	@property
	def chunked(self):
		return self.body.chunked or self.headers.get("Transfer-Encoding") == 'chunked'

	@chunked.setter
	def chunked(self, chunked):
		self.body.chunked = chunked
		if chunked:
			self.headers['Transfer-Encoding'] = 'chunked'
			self.headers.pop('Content-Length', None)
		else:
			self.headers.pop('Transfer-Encoding', None)

	def __repr__(self):
		return '<HTTP Message(protocol=%s)>' % (self.protocol,)


class Request(Message):
	u"""A HTTP request message

		.. seealso:: :rfc:`2616#section-5`
	"""

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
			raise InvalidLine(line.decode('ISO8859-1'))

		# protocol version
		super(Request, self).parse(bits[2])

		# method
		self.method.parse(bits[0])

		# URI
		try:
			self.uri.parse(bits[1])
		except InvalidURI as exc:
			raise InvalidLine(u"Invalid request URL: %r" % Unicode(exc))

	def compose(self):
		u"""composes the request line"""
		return b"%s %s %s\r\n" % (bytes(self.__method), bytes(self.__uri), bytes(self.protocol))

	def prepare(self):
		if self.body:
			self.headers['Content-Length'] = bytes(len(self.body))

		self.chunked = self.chunked

		self.close = self.close

		if self.method in ('PUT', 'POST') and self.body:
			self.headers['Date'] = bytes(Date())  # RFC 2616 Section 14.18

	@property
	def close(self):
		return self.headers.get('Connection') == 'close'

	@close.setter
	def close(self, close):
		if close:
			self.headers['Connection'] = 'close'
		else:
			self.headers.pop('Connection', None)

	def __bytes__(self):
		return self.compose()

	def __repr__(self):
		return "<HTTP Request(%s %s %s)>" % (bytes(self.__method), bytes(self.__uri.path), bytes(self.protocol))


class Response(Message):
	u"""A HTTP response message

		.. seealso:: :rfc:`2616#section-6`
	"""

	@property
	def status(self):
		return self.__status

	@status.setter
	def status(self, status):
		self.__status.set(status)

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
			raise InvalidLine(line.decode('ISO8859-1'))

		# version
		super(Response, self).parse(bits[0])

		# status
		self.status.parse(bits[1])

	def compose(self):
		u"""composes the response line"""
		return b"%s %s\r\n" % (bytes(self.protocol), bytes(self.status))

	def prepare(self, request=None):
		u"""prepares the response for being ready for transmitting"""

		status = self.status
		if status < 200 or status in (204, 205, 304):
			# 1XX, 204 NO_CONTENT, 205 RESET_CONTENT, 304 NOT_MODIFIED
			self.body = None

		self.chunked = self.chunked
		if not self.chunked:
			self.headers['Content-Length'] = bytes(len(self.body))

		self.headers['Date'] = bytes(Date())  # RFC 2616 Section 14.18

		# remove header which should not occur along with this status
		if int(status) in STATUSES:
			for header in STATUSES[int(status)].header_to_remove:
				self.headers.pop(header, None)

		self.close = self.close

		if request is None:
			return

		if request.headers.get('Connection') == 'close':
			self.close = True  # RFC 2616 Section 14.10

		if request.method == 'HEAD':
			self.body = None  # RFC 2616 Section 9.4

	@property
	def close(self):
		# TODO: 100 Continue
		if self.status == 413:
			# 413 Request Entity Too Large
			# RFC 2616 Section 10.4.14
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
		if close:
			if self.protocol >= (1, 1):
				self.headers['Connection'] = 'close'
				return
		else:
			if self.protocol < (1, 1):
				self.headers['Connection'] = 'keep-alive'
				return
		self.headers.pop('Connection', None)

	def __bytes__(self):
		return self.compose()

	def __repr__(self):
		# TODO: do we really want to check the body length here?
		content_type = self.headers.get("Content-Type", "")
		return "<HTTP Response(%d %s (%d))>" % (self.status, content_type, len(self.body))
