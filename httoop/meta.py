"""MetaClasses for HTTOOP types

"""

from httoop.util import Unicode, PY3

__all__ = ['HTTPType']


class HTTPSemantic(object):
	def __str__(self):
		if PY3:
			return self.__unicode__()
		else:
			return self.__bytes__()

	def __unicode__(self):
		bstr = bytes(self)
		try:
			return bstr.decode('UTF-8')
		except UnicodeDecodeError:
			return bstr.decode('ISO8859-1')

	def __bytes__(self):
		return self.compose()

	def parse(self, data):
		raise NotImplemented

	def compose(self):
		raise NotImplemented

	def __cmp__(self, other):
		if isinstance(other, Unicode):
			return cmp(Unicode(self), other)
		return cmp(bytes(self), other)

	def __hash__(self):
		return bytes(self).__hash__()


class HTTPType(type):
	def __new__(mcs, name, bases, dict):
		bases = list(bases)
		if object in bases:
			bases.remove(object)
		bases.append(HTTPSemantic)
		return type.__new__(mcs, name, tuple(bases), dict)
