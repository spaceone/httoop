"""MetaClasses for HTTOOP types

"""

from httoop.util import Unicode, PY3

__all__ = ['HTTPSemantic']


class HTTPSemantic(type):
	u"""Implements the HTTP Semantic interface"""

	def __new__(mcs, name, bases, dict_):
		def setdefault(name, method):
			for base in bases:
				if base in (object, Exception):
					continue
				if name in dir(base):
					return
			dict_.setdefault(name, method)

		def __str__(self):
			if PY3:
				return self.__unicode__()
			else:
				return self.__bytes__()
		setdefault('__str__', __str__)

		def __unicode__(self):
			bstr = bytes(self)
			try:
				return bstr.decode('UTF-8')
			except UnicodeDecodeError:
				return bstr.decode('ISO8859-1')
		setdefault('__unicode__', __unicode__)

		def __bytes__(self):
			return self.compose()
		setdefault('__bytes__', __bytes__)

		def parse(self, data):
			raise NotImplementedError
		setdefault('parse', parse)

		def compose(self):
			raise NotImplementedError
		setdefault('compose', compose)

		def __cmp__(self, other):
			if isinstance(other, Unicode):
				return cmp(Unicode(self), other)
			return cmp(bytes(self), other)
		setdefault('__cmp__', __cmp__)

		def __hash__(self):
			return bytes(self).__hash__()
		setdefault('__hash__', __hash__)

		def __repr__(self):
			return '<HTTP %s>' % (self.__class__.__name__)
		setdefault('__repr__', __repr__)

		# python 2/3 unifying
		if '__bool__' in dict_ or '__nonzero__' in dict_:
			dict_.setdefault('__bool__', dict_.get('__nonzero__'))
			dict_.setdefault('__nonzero__', dict_.get('__bool__'))

		return type.__new__(mcs, name, tuple(bases), dict_)
