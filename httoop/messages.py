# -*- coding: utf-8 -*-
"""HTTP request and response messages

.. seealso:: :rfc:`2616#section-4`
"""

__all__ = ['Message', 'Request', 'Response', 'Protocol']

import re

from httoop.headers import Headers
from httoop.status import Status
from httoop.body import Body
from httoop.uri import URI

# TODO: replace @property by __set__ and  __get__ in the specific classes
# TODO: add __slots__ for request and response to gain performance
# TODO: rename get and set?
# TODO: recheck the regex if they are completely HTTP comform, but they should be
# TODO: create a ResponseBody for chunked response

class InvalidLine(ValueError):
	u"""error raised when first line is invalid"""

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

class Message(object):
	u"""A HTTP message

		.. seealso:: :rfc:`2616#section-4`
	"""

	VERSION_RE = re.compile(r"^HTTP/(\d+).(\d+)$")

	@property
	def protocol(self):
		return self._protocol

	@protocol.setter
	def protocol(self, protocol):
		self._protocol = Protocol(protocol)

	# alias
	version = protocol

	headers = Headers()
	body = Body()

	def __init__(self, protocol=None, headers=None, body=None):
		u"""Initiates a new Message to hold information about the message.

			:param protocol: the requested protocol
			:type  protocol: str

			:param headers: the request headers
			:type  headers: dict or :class:`Headers`

			:param body: the request body
			:type  body: any
		"""
		self._protocol = Protocol(protocol or (1, 1))
		self.__headers = Headers(headers or {})
		self.__body = Body(body or b'')

	def parse(self, version):
		u"""parses the HTTP protocol version

			:param version: the version string
			:type  version: bytes
		"""
		match = self.VERSION_RE.match(version)
		if match is None:
			raise InvalidLine("Invalid HTTP version: %s" % version)

		self.protocol = (int(match.group(1)), int(match.group(2)))

class Request(Message):
	u"""A HTTP request message

		.. seealso:: :rfc:`2616#section-5`
	"""

	METHOD_RE = re.compile(r"^[A-Z0-9$-_.]{1,20}$")

	@property
	def method(self):
		return self._method

	@method.setter
	def method(self, method):
		self._method = method

	uri = URI()

	def __init__(self, method=None, uri=None, protocol=None, headers=None, body=None):
		"""Creates a new Request object to hold information about a request.

			:param method: the requested method
			:type  method: str

			:param uri: the requested URI
			:type  uri: str or :class:`URI`

		"""

		super(Request, self).__init__(protocol, headers, body)
		self._method = method or 'GET'
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
		super(Request, self).__init__(bits[2])

		# method
		if None is self.METHOD_RE.match(bits[0]):
			raise InvalidLine("invalid Method: %s" % bits[0])
		self.method = bits[0] # HTTP method is case sensitive

		# URI
		self.uri = bits[1]
		if self.__uri.fragment or self.__uri.username or self.__uri.password:
			raise InvalidLine("Invalid request URI. "\
				"HTTP request URIs MUST NOT contain fragments, "\
				"username or password")
		# TODO: do something like uri.validate() or raise FooBar

	def compose(self):
		u"""composes the request line"""
		return b"%s %s %s" % (bytes(self._method), bytes(self.__uri), bytes(self._protocol))

	def __repr__(self):
		return "<HTTP Request %s %s %s>" % (bytes(self._method), bytes(self.__uri.path), bytes(self.protocol))

class Response(Message):
	u"""A HTTP response message

		.. seealso:: :rfc:`2616#section-6`
	"""

	STATUS_RE = re.compile(r"^(\d{3})(?:\s+([\s\w]*))$")

	status = Status()

	def __init__(self, status=None, protocol=None, headers=None, body=None):
		"""Creates a new Response object to hold information about the response.

			:param status: A HTTP status, default is 200
			:type status: int or str or :class:`Status`
		"""

		super(Response, self).__init__(protocol, headers, body)
		# TODO: overwrite the body by an body which has also chunked TE, stream, ...

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
			raise InvalidLine("Invalid status %s" % bits[1])

		self.status = (int(match.group(1)), match.group(2))

	def compose(self):
		u"""composes the response line"""
		return b"%s %s" % (bytes(self.protocol), bytes(self.status))

	def __repr__(self):
		# TODO: do we really want to check the body length here?
		content_type = self.headers.get("Content-Type", "")
		return "<HTTP Response %d %s (%d)>" % (self.status, content_type, len(self.body))
