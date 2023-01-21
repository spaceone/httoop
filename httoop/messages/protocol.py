# -*- coding: utf-8 -*-
"""HTTP request and response messages.

.. seealso:: :rfc:`2616#section-4`
"""

import re
from typing import Any, Tuple, Union

from httoop.exceptions import InvalidLine
from httoop.meta import HTTPSemantic
from httoop.six import with_metaclass
from httoop.util import Unicode, _

__all__ = ('Protocol', )


class Protocol(with_metaclass(HTTPSemantic)):
	u"""The HTTP protocol version."""

	__slots__ = ('name', '__protocol')

	@property
	def version(self) -> Tuple[int, int]:
		return tuple(self)

	@property
	def major(self) -> int:
		return self[0]

	@property
	def minor(self) -> int:
		return self[1]

	PROTOCOL_RE = re.compile(br"^(HTTP)/(\d+)\.(\d+)\Z")

	def __init__(self, protocol: Union[bytes, "Protocol", Tuple[int, int], int, str]=(1, 1)) -> None:
		self.__protocol = protocol
		self.name = b'HTTP'
		self.set(protocol)

	def set(self, protocol: Union[bytes, "Protocol", Tuple[int, int], int, str]) -> None:
		if isinstance(protocol, (bytes, Unicode)):
			if isinstance(protocol, Unicode):
				protocol = protocol.encode('ascii', 'replace')
			protocol = self.parse(protocol)
		else:
			major, minor = tuple(protocol)
			self.__protocol = (int(major), int(minor))

	def parse(self, protocol: bytes) -> None:
		match = self.PROTOCOL_RE.match(protocol)
		if match is None:
			raise InvalidLine(_(u"Invalid HTTP protocol: %r"), protocol.decode('ISO8859-1'))
		self.__protocol = (int(match.group(2)), int(match.group(3)))
		self.name = match.group(1)

	def compose(self) -> bytes:
		return b'%s/%d.%d' % (self.name, self.major, self.minor)

	def __iter__(self):
		return self.__protocol.__iter__()

	def __getitem__(self, key: int) -> int:
		return self.version[key]

	def __eq__(self, other: Any) -> bool:
		try:
			other = Protocol(other)
		except (TypeError, InvalidLine):
			if isinstance(other, int):
				return self.major == other
			return False
		return self.version == other.version

	def __lt__(self, other: Union[int, Tuple[int, int], "Protocol"]) -> bool:
		try:
			other = Protocol(other)
		except (TypeError, InvalidLine):
			if isinstance(other, int):
				return self.major < other
			raise  # pragma: no cover
		return self.version < other.version

	def __gt__(self, other: Union[int, Tuple[int, int], "Protocol"]) -> bool:
		try:
			other = Protocol(other)
		except (TypeError, InvalidLine):
			if isinstance(other, int):
				return self.major > other
			raise  # pragma: no cover
		return self.version > other.version
