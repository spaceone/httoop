"""MetaClasses for HTTOOP types."""

from __future__ import absolute_import

from typing import Any, Dict, Tuple, Type, Union

from httoop.util import PY3, Unicode

__all__ = ['HTTPSemantic']


class Semantic(object):

	__slots__ = ()

	def __str__(self) -> str:
		return self.__unicode__() if PY3 else self.__bytes__()

	def __unicode__(self) -> str:
		return bytes(self).decode(getattr(self, 'encoding', 'ISO8859-1'))

	def __bytes__(self) -> bytes:
		return self.compose()

	def parse(self, data):  # pragma: no cover
		raise NotImplementedError('%s.parse(%.5r)' % (type(self).__name__, data))

	def compose(self):  # pragma: no cover
		raise NotImplementedError('%s.compose()' % (type(self).__name__, ))

	def __eq__(self, other: Any) -> bool:
		if isinstance(other, Unicode):
			return Unicode(self) == other
		return bytes(self) == other

	def __ne__(self, other: Any) -> bool:
		return not self == other

	def __ge__(self, other: Union[int, Tuple[int, int]]) -> bool:
		return self == other or self > other

	def __le__(self, other: Union[int, Tuple[int, int]]) -> bool:
		return self == other or self < other

	def __format__(self, format_spec):
		return format(str(self), format_spec)

	def __repr__(self) -> str:
		return '<HTTP %s(0x%x)>' % (self.__class__.__name__, id(self))


class HTTPSemantic(type):
	u"""Implements the HTTP Semantic interface."""

	def __new__(mcs: Type, name: str, bases: Any, dict_: Dict[str, Any]) -> Any:
		bases = list(bases)
		if object in bases:
			bases.remove(object)
		bases.append(Semantic)

		# python 2/3 unifying
		if '__bool__' in dict_ or '__nonzero__' in dict_:
			dict_.setdefault('__bool__', dict_.get('__nonzero__'))
			dict_.setdefault('__nonzero__', dict_.get('__bool__'))

		return super(HTTPSemantic, mcs).__new__(mcs, name, tuple(bases), dict_)
