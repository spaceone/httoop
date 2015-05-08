# -*- coding: utf-8 -*-
"""HTTP request and response messages

.. seealso:: :rfc:`2616#section-4`
"""

__all__ = ('Message')

from httoop.messages.body import Body
from httoop.messages.protocol import Protocol

from httoop.header import Headers
from httoop.meta import HTTPSemantic


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

	def __hash__(self):
		return id(self).__hash__()

	def __repr__(self):
		return '<HTTP Message(protocol=%s)>' % (self.protocol,)
