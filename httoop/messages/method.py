# -*- coding: utf-8 -*-
"""HTTP request and response messages

.. seealso:: :rfc:`2616#section-4`
"""

import re

from httoop.exceptions import InvalidLine
from httoop.meta import HTTPSemantic
from httoop.six import with_metaclass
from httoop.util import Unicode, _

__all__ = ('Method', )


class Method(with_metaclass(HTTPSemantic)):
	u"""A HTTP request method"""
	__slots__ = ('__method')

	@property
	def safe(self):
		return self in self.safe_methods

	@property
	def idempotent(self):
		return self in self.idempotent_methods

	safe_methods = (u'GET', u'HEAD', u'SEARCH')
	idempotent_methods = (u'GET', u'HEAD', u'PUT', u'DELETE', u'OPTIONS', u'TRACE', u'SEARCH')
	METHOD_RE = re.compile(br"^[A-Z0-9$-_.]{1,20}\Z", re.IGNORECASE)

	def __init__(self, method=None):
		self.set(method or u'GET')

	def __hash__(self):
		return hash(bytes(self))

	def set(self, method):
		if isinstance(method, Unicode):
			method = method.encode('ASCII')
		self.parse(method)

	def parse(self, method):
		if not self.METHOD_RE.match(method):
			raise InvalidLine(_(u"Invalid method: %r"), method.decode('ISO8859-1'))
		self.__method = method

	def compose(self):
		return self.__method
