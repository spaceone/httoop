# -*- coding: utf-8 -*-
"""HTTP status codes

.. seealso:: :rfc:`2616#section-10`"""

from httoop.messages import Body  # TODO: remove ?
from httoop.status.status import Status, REASONS
from httoop.util import iteritems
from httoop.meta import HTTPSemantic

# TODO: create HTTPEntity ?
# TODO: inherit from response?
# TODO: also inherit from circuits.Event/SF.http.server.Response,
# implement __call__ for additional arguments then?
class HTTPStatusException(Status, Exception):
	u"""This class represents a small HTTP Response message
		for error handling purposes"""

	@property
	def headers(self):
		return self._headers

	@property
	def body(self):
		if not hasattr(self, '_body'):
			self._body = Body(mimetype='application/json')
			self._body.data = self.to_dict()
		return self._body

	@body.setter
	def body(self, value):
		self.body
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

		Status.__init__(self, self.__class__.code, reason=reason)

		self._headers = dict()
		self._traceback = None

		if isinstance(headers, dict):
			self._headers.update(headers)

		if description is not None:
			self.description = description

		if traceback:
			self.traceback = traceback

	def __repr__(self):
		return '<HTTP Status %d %r>' % (int(self), self.reason)

	__str__ = __repr__

	def to_dict(self):
		u"""the default body arguments"""
		return dict(status=self.status,
		            reason=self.reason,
		            description=self.description,
		            headers=self.headers)


class HTTPInformational(HTTPStatusException):
	u"""INFORMATIONAL = 1xx
		Mostly used for negotiation with the HTTP Server
	"""
	pass


class HTTPSuccess(HTTPStatusException):
	u"""SUCCESS = 2xx
		indicates that an operation was successful.
	"""
	pass


class HTTPRedirect(HTTPStatusException):
	u"""REDIRECTIONS = 3xx
		A redirection to other URI(s) which are set in the Location-header.
	"""
	location = None
	u"""TODO"""

	def __init__(self, location, *args, **kwargs):
		kwargs.setdefault('headers', {})['Location'] = location
		super(HTTPRedirect, self).__init__(*args, **kwargs)

	def to_dict(self):
		dct = super(HTTPRedirect, self).to_dict()
		if self.headers.get('Location'):
			dct.update(dict(Location=self.headers['Location']))
		return dct


class HTTPClientError(HTTPStatusException):
	u"""CLIENT_ERRORS = 4xx
		Something is wrong with the client: e.g. authentication,
		format of wanted representation, or error in the clients http library.
	"""
	pass


class HTTPServerError(HTTPStatusException):
	u"""SERVER_ERRORS = 5xx
		Indicates that something gone wrong on the server side.
		The server can send the Retry-After header if
		it knows that the problem is temporary.
	"""
	def to_dict(self):
		dct = super(HTTPServerError, self).to_dict()
		dct.update(dict(traceback=self.traceback or ""))
		return dct


class StatusType(HTTPSemantic):
	def __new__(mcs, name, bases, dict_):
		code = int(dict_['code'])
		if 99 < code < 200:
			scls = HTTPInformational
		elif code < 300:
			scls = HTTPSuccess
		elif code < 400:
			scls = HTTPRedirect
		elif code < 500:
			scls = HTTPClientError
		elif code < 600:
			scls = HTTPServerError
		else:
			raise ValueError('A HTTP Status code can not be greater than 599 or lower than 100')

		reason = REASONS.get(code, ('', ''))
		dict_.setdefault('reason', reason[0])
		dict_.setdefault('description', reason[1])
		dict_.setdefault('__str__', HTTPStatusException.__str__)  # TODO: remove metaclass / inheritance
		return super(StatusType, mcs).__new__(mcs, name, (scls,), dict_)
