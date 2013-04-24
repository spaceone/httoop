# -*- coding: utf-8 -*-
"""HTTP status codes

.. seealso:: :rfc:`2616#section-10`
"""

class Status(object):
	u"""A HTTP status code"""

	__slots__ = ['status', 'reason']

	def __init__(self, status=None, reason=None):
		self.status = 0
		if status:
			self.set(status)
		self.reason = reason or self.reason or REASONS.get(status, ('', ''))[0]

	def __str__(self):
		return '%d %s' % (self.status, self.reason)

	def __int__(self):
		return self.status

	def __eq__(self, other):
		if isinstance(other, int):
			return self.status == other
		return super(Status, self).__eq__(other)

	def __lt__(self, other):
		if isinstance(other, int):
			return self.status < other
		return super(Status, self).__lt__(other)

	def __gt__(self, other):
		if isinstance(other, int):
			return self.status > other
		return super(Status, self).__gt__(other)

	def set(self, status):
		u"""sets reason and status

			:param status:
				A status, e.g.: 200, (200, 'OK'), '200 OK'
			:type  status:
				int or tuple or bytes or Status
		"""
		if isinstance(status, int):
			self.status, self.reason = status, REASONS.get(status, ('', ''))[0]
		elif isinstance(status, tuple):
			self.status, self.reason = status
		elif isinstance(status, bytes): # FIXME: python3
			_status, _reason = status.split(None, 1)
			self.status, self.reason = int(_status), _reason
		elif isinstance(status, Status):
			self.status, self.reason = status.status, status.reason
		else:
			raise ValueError('invalid type for an HTTP status code')

	def __repr__(self):
		# TODO: ?
		return '<HTTP Status (status=%d, reason=%r)>' % (self.status, self.reason)

# ripped from pythons BaseHTTPServer, dunno what license it is
REASONS = {
	# status: (reason, description)
	100: ('Continue', 'Request received, please continue'),
	101: ('Switching Protocols', 'Switching to new protocol; obey Upgrade header'),
	200: ('OK', 'Request fulfilled, document follows'),
	201: ('Created', 'Document created, URL follows'),
	202: ('Accepted', 'Request accepted, processing continues off-line'),
	203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
	204: ('No Content', 'Request fulfilled, nothing follows'),
	205: ('Reset Content', 'Clear input form for further input.'),
	206: ('Partial Content', 'Partial content follows.'),
	300: ('Multiple Choices', 'Object has several resources -- see URI list'),
	301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
	302: ('Found', 'Object moved temporarily -- see URI list'),
	303: ('See Other', 'Object moved -- see Method and URL list'),
	304: ('Not Modified', 'Document has not changed since given time'),
	305: ('Use Proxy', 'You must use proxy specified in Location to access this resource.'),
	307: ('Temporary Redirect', 'Object moved temporarily -- see URI list'),
	400: ('Bad Request', 'Bad request syntax or unsupported method'),
	401: ('Unauthorized', 'No permission -- see authorization schemes'),
	402: ('Payment Required', 'No payment -- see charging schemes'),
	403: ('Forbidden', 'Request forbidden -- authorization will not help'),
	404: ('Not Found', 'Nothing matches the given URI'),
	405: ('Method Not Allowed', 'Specified method is invalid for this resource.'),
	406: ('Not Acceptable', 'URI not available in preferred format.'),
	407: ('Proxy Authentication Required', 'You must authenticate with this proxy before proceeding.'),
	408: ('Request Timeout', 'Request timed out; try again later.'),
	409: ('Conflict', 'Request conflict.'),
	410: ('Gone', 'URI no longer exists and has been permanently removed.'),
	411: ('Length Required', 'Client must specify Content-Length.'),
	412: ('Precondition Failed', 'Precondition in headers is false.'),
	413: ('Request Entity Too Large', 'Entity is too large.'),
	414: ('Request-URI Too Long', 'URI is too long.'),
	415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
	416: ('Requested Range Not Satisfiable', 'Cannot satisfy request range.'),
	417: ('Expectation Failed', 'Expect condition could not be satisfied.'),
	500: ('Internal Server Error', 'The server encountered an unexpected condition which prevented it from fulfilling the request.'),
	501: ('Not Implemented', 'Server does not support this operation'),
	502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
	503: ('Service Unavailable', 'The server is currently unable to handle the request due to a temporary overloading or maintenance of the server.'),
	504: ('Gateway Timeout', 'The gateway server did not receive a timely response'),
	505: ('HTTP Version Not Supported', 'Cannot fulfill request.')
}
