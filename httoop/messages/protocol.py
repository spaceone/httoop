# -*- coding: utf-8 -*-
"""HTTP request and response messages

.. seealso:: :rfc:`2616#section-4`
"""

__all__ = ('Protocol',)

import re

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

	def __eq__(self, other):
		try:
			other = Protocol(other)
		except (TypeError, InvalidLine):
			if isinstance(other, int):
				return self.major == other
			return False
		return self.version == other.version

	def __ne__(self, other):
		return not (self == other)

	def __lt__(self, other):
		try:
			other = Protocol(other)
		except (TypeError, InvalidLine):
			if isinstance(other, int):
				return self.major < other
			raise  # pragma: no cover
		return self.version < other.version

	def __gt__(self, other):
		try:
			other = Protocol(other)
		except (TypeError, InvalidLine):
			if isinstance(other, int):
				return self.major > other
			raise  # pragma: no cover
		return self.version > other.version

	def __ge__(self, other):
		return self == other or self > other

	def __le__(self, other):
		return self == other or self < other