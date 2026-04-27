"""MetaClasses for HTTOOP types."""

from __future__ import annotations

from typing import Any


__all__ = ['HTTPSemantic']


class Semantic:

    __slots__ = ()

    def __str__(self) -> str:
        return bytes(self).decode(getattr(self, 'encoding', 'ISO8859-1'))

    def __bytes__(self) -> bytes:
        return self.compose()

    def parse(self, data):  # pragma: no cover
        raise NotImplementedError('%s.parse(%.5r)' % (type(self).__name__, data))

    def compose(self):  # pragma: no cover
        raise NotImplementedError(f'{type(self).__name__}.compose()')

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return str(self) == other
        return bytes(self) == other

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __ge__(self, other: int | tuple[int, int]) -> bool:
        return self == other or self > other

    def __le__(self, other: int | tuple[int, int]) -> bool:
        return self == other or self < other

    def __format__(self, format_spec) -> str:
        return format(str(self), format_spec)

    def __repr__(self) -> str:
        return f'<HTTP {self.__class__.__name__}(0x{id(self):x})>'


class HTTPSemantic(type):
    """Implements the HTTP Semantic interface."""

    def __new__(mcs: type, name: str, bases: Any, dict_: dict[str, Any]) -> Any:
        bases = list(bases)
        if object in bases:
            bases.remove(object)
        bases.append(Semantic)

        return super().__new__(mcs, name, tuple(bases), dict_)
