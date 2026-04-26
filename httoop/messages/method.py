"""
HTTP request and response messages.

.. seealso:: :rfc:`2616#section-4`
"""
from __future__ import annotations

import re
from typing import Optional

from httoop.exceptions import InvalidLine
from httoop.meta import HTTPSemantic
from httoop.six import with_metaclass
from httoop.util import Unicode, _


__all__ = ('Method', )


class Method(with_metaclass(HTTPSemantic)):
    """A HTTP request method."""

    __slots__ = ('__method')

    @property
    def safe(self) -> bool:
        return self in self.safe_methods

    @property
    def idempotent(self) -> bool:
        return self in self.idempotent_methods

    safe_methods = ('GET', 'HEAD', 'SEARCH')
    idempotent_methods = ('GET', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'TRACE', 'SEARCH')
    METHOD_RE = re.compile(br'^[A-Z0-9$-_.]{1,20}\Z', re.IGNORECASE)

    def __init__(self, method: Optional[str] = None) -> None:
        self.set(method or 'GET')

    def __hash__(self) -> int:
        return hash(bytes(self))

    def set(self, method: str) -> None:
        if isinstance(method, Unicode):
            method = method.encode('ASCII')
        self.parse(method)

    def parse(self, method: bytes) -> None:
        if not self.METHOD_RE.match(method):
            raise InvalidLine(_('Invalid method: %r'), method.decode('ISO8859-1'))
        self.__method = method

    def compose(self) -> bytes:
        return self.__method
