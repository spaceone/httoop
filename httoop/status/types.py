# -*- coding: utf-8 -*-
"""HTTP status codes

.. seealso:: :rfc:`2616#section-10`"""

from httoop.six import with_metaclass

from httoop.status.status import Status, REASONS
from httoop.meta import HTTPSemantic


class StatusType(HTTPSemantic):

	def __new__(mcs, name, bases, dict_):
		code = int(dict_.get('code', 0))
		if 99 < code < 200:
			scls = 'InformationalStatus'
		elif code < 300:
			scls = 'SuccessStatus'
		elif code < 400:
			scls = 'RedirectStatus'
		elif code < 500:
			scls = 'ClientErrorStatus'
		elif code < 600:
			scls = 'ServerErrorStatus'
		else:
			raise RuntimeError('A HTTP Status code can not be greater than 599 or lower than 100')

		if code and not any(scls == base.__name__ for base in bases):
			raise RuntimeError('%s must inherit from %s' % (name, scls))

		reason = REASONS.get(code, ('', ''))
		dict_.setdefault('reason', reason[0])
		dict_.setdefault('description', reason[1])
		return super(StatusType, mcs).__new__(mcs, name, bases, dict_)


class StatusException(with_metaclass(StatusType, Status, Exception)):
	u"""This class represents a small HTTP Response message
		for error handling purposes"""

	@property
	def headers(self):
		return self._headers

	@property
	def body(self):
		if not hasattr(self, '_body'):
			from httoop.messages.body import Body
			self._body = Body(mimetype='application/json')
			self._body.data = self.to_dict()
		return self._body

	@body.setter
	def body(self, value):
		self.body  # pylint: disable=W0104
		self._body.set(value)

	header_to_remove = ()
	u"""a tuple of header field names which should be
		removed when responding with this error"""

	description = ''

	@property
	def traceback(self):
		return self._traceback

	@traceback.setter
	def traceback(self, tb):
		if self.server_error:
			self._traceback = tb

	code = 0

	def __init__(self, description=None, reason=None, headers=None, traceback=None):
		u"""
			:param description:
				a description of the error which happened
			:type description: str

			:param reason:
				a additional reason phrase
			:type reason: str

			:param headers:
			:type headers: dict

			:param traceback:
				A Traceback for the error
			:type traceback: str
		"""

		Status.__init__(self, self.__class__.code, reason=reason)  # pylint: disable=W0233

		self._headers = dict()
		self._traceback = None

		if isinstance(headers, dict):
			self._headers.update(headers)

		if description is not None:
			self.description = description

		if traceback:
			self.traceback = traceback

	def __repr__(self):
		description = ''
		if self.description:
			description = '(%s)' % (self.description,)
		return '<HTTP Status %d %r %s>' % (int(self), self.reason, description)

	__str__ = __repr__

	def to_dict(self):
		u"""the default body arguments"""
		return dict(
			status=self.status,
			reason=self.reason,
			description=self.description,
			headers=self.headers
		)
