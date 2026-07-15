"""
HTTP request and response messages.

.. seealso:: :rfc:`2616#section-4`
"""

from __future__ import annotations

import re

from httoop.exceptions import InvalidLine
from httoop.meta import Semantic
from httoop.util import _, integer


__all__ = ('Protocol',)


class Protocol(Semantic):
    """The HTTP protocol version."""

    __slots__ = ('__protocol', 'name')

    @property
    def version(self) -> tuple[int, int]:
        return tuple(self)

    @property
    def major(self) -> int:
        return self[0]

    @property
    def minor(self) -> int:
        return self[1]

    PROTOCOL_RE = re.compile(rb'^(HTTP)/(\d+)\.(\d+)\Z')

    def __init__(self, protocol: bytes | Protocol | tuple[int, int] | int | str = (1, 1)) -> None:
        self.__protocol = protocol
        self.name = b'HTTP'
        self.set(protocol)

    def set(self, protocol: bytes | Protocol | tuple[int, int] | int | str) -> None:
        if isinstance(protocol, (bytes, str)):
            if isinstance(protocol, str):
                protocol = protocol.encode('ascii', 'replace')
            protocol = self.parse(protocol)
        else:
            major, minor = tuple(protocol)
            self.__protocol = (integer(major), integer(minor))

    def parse(self, protocol: bytes) -> None:
        match = self.PROTOCOL_RE.match(protocol)
        if match is None:
            raise InvalidLine(_('Invalid HTTP protocol: %r'), protocol.decode('ISO8859-1'))
        self.name, major, minor = match.groups()
        try:
            self.__protocol = (integer(major), integer(minor))
        except ValueError:
            raise InvalidLine(_('Invalid HTTP protocol: %r'), protocol.decode('ISO8859-1')) from None

    def compose(self) -> bytes:
        return b'%s/%d.%d' % (self.name, self.major, self.minor)

    def __iter__(self):
        return self.__protocol.__iter__()

    def __getitem__(self, key: int) -> int:
        return self.version[key]

    def __eq__(self, other: object) -> bool:
        try:
            other = Protocol(other)
        except (TypeError, InvalidLine):
            if isinstance(other, int):
                return self.major == other
            return False
        return self.version == other.version

    def __lt__(self, other: int | tuple[int, int] | Protocol) -> bool:
        try:
            other = Protocol(other)
        except (TypeError, InvalidLine):
            if isinstance(other, int):
                return self.major < other
            raise  # pragma: no cover
        return self.version < other.version

    def __gt__(self, other: int | tuple[int, int] | Protocol) -> bool:
        try:
            other = Protocol(other)
        except (TypeError, InvalidLine):
            if isinstance(other, int):
                return self.major > other
            raise  # pragma: no cover
        return self.version > other.version
