# -*- coding: utf-8 -*-
"""HTTP request and response messages

.. seealso:: :rfc:`2616#section-4`
"""

from httoop.exceptions import InvalidLine
from httoop.messages.message import Message
from httoop.status import Status
from httoop.util import _

__all__ = ('Response', )


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
			raise InvalidLine(_(u'Invalid response line: %r'), line.decode('ISO8859-1'))

		# version
		super(Response, self).parse(version)

		# status
		self.status.parse(status)

	def compose(self):
		u"""composes the response line"""
		return b"%s %s\r\n" % (bytes(self.protocol), bytes(self.status))

	def __repr__(self):
		return "<HTTP Response(%d %s)>" % (self.status, self.body.mimetype)
