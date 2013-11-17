# -*- coding: utf-8 -*-
"""HTTP status codes

.. seealso:: :rfc:`2616#section-10`"""

from httoop.body import Body  # TODO: remove ?
from httoop.status import Status, REASONS
from httoop.util import iteritems
from httoop.meta import HTTPSemantic

# mapping of status -> Class, will be filled at the bottom
STATUSES = dict()


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
		return '<HTTP<%s>(%s)>' % (self.__class__.__name__, ' '.join('%s=%r' % (k, v) for k, v in iteritems(self.to_dict())))

	def to_dict(self):
		u"""the default body arguments"""
		return dict(status=self.status,
		            reason=self.reason,
		            description=self.description,
		            traceback=self.traceback or "",
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
		dct.update(dict(traceback=self.traceback))
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
		return super(StatusType, mcs).__new__(mcs, name, (scls,), dict_)


class CONTINUE(object):
	u"""This is, beside 417, the code for a LBYL (Look before you leap) request.
		It indicates that the request is OK and the client should resent its request.

		.. seealso:: :rfc:`2616#section-10.1`"""
	__metaclass__ = StatusType
	code = 100
	body = None


class SWITCHING_PROTOCOLS(object):
	u"""If the client wants to use another protocol (in the Upgrade-header)
		this is the response that the TCP server now speaks another protocol.
	"""
	__metaclass__ = StatusType
	code = 101
	body = None

#class PROCESSING(object):
#	__metaclass__ = StatusType
#	code = 102


class OK(object):
	u"""The request was successful.
		On GET requests the entity body will be a
		representation of the requested resource.
		For other methods the entity body contains a representation of
		the current state of the resource or a description of the performed action
	"""
	__metaclass__ = StatusType
	code = 200


class CREATED(object):
	u"""A new resource was created.
		This should only be send on POST and PUT requests.
		The Location-Header should contain the URI to the created resource.
		The entity-body should describe and link to the created resource.
	"""
	__metaclass__ = StatusType
	code = 201

	def __init__(self, location, *args, **kwargs):
		kwargs.setdefault('headers', {})['Location'] = location
		super(CREATED, self).__init__(*args, **kwargs)

	def to_dict(self):
		dct = super(CREATED, self).to_dict()
		dct.update(dict(Location=self.headers['Location']))
		return dct


class ACCEPTED(object):
	u"""The request looks valid but will be procecced later.
		It is an asynchronous action.
		The Location-Header should contain a URI where
		the status of processing can be found.
		If this is not possible it should give an estimate
		time when the request will be processed."""
	__metaclass__ = StatusType
	code = 202


class NON_AUTHORITATIVE_INFORMATION(object):
	u"""Everything is OK but the response headers
		may be altered by a third party."""
	__metaclass__ = StatusType
	code = 203


class NO_CONTENT(object):
	u"""GET: The representation of the resource is empty.
		other request methods: the status message or representation is not needed.
		This is useful for ajax requests.
		It is also useful for making series of edits
		to a single record (a HTML POST form)."""
	__metaclass__ = StatusType
	code = 204
	body = None


class RESET_CONTENT(object):
	u"""The same as 204 but this indicated that the client should
		reset the view of its data structure.
		This is useful for entering a series of records
		in succession (a HTML POST form).
	"""
	__metaclass__ = StatusType
	code = 205
	body = None


class PARTIAL_CONTENT(object):
	u"""Partial GET:
		The response does not contain the full representation of a resource
		but only the bytes requested in the Content-Range-header.
		It is often use to resume an interrupted download.
		The Date-header is required, the ETag-header
		and Content-Location-header are useful.
	"""
	__metaclass__ = StatusType
	code = 206

#class MULTI_STATUS(object):
#	__metaclass__ = StatusType
#	code = 207

	#"""This status code indicated that the entity-body contains information
	#about the states of the batch request.
	#It is not an official HTTP-Status-Code: WebDAV
	#It is not realy RESTful to use.
	#The entity-body is descripted in RFC 2518."""

#class ALREADY_REPORTED(object):
#	__metaclass__ = StatusType
#	code = 208


#class IM_USED(object):
#	__metaclass__ = StatusType
#	code = 226


class MULTIPLE_CHOICES(object):
	u"""The server has multiple representations of the requested resource.
		And the client e.g. did not specify the Accept-header or
		the requested representation does not exists.
	"""
	__metaclass__ = StatusType
	code = 300

	def __init__(self, locations, *args, **kwargs):
		if isinstance(locations, basestring):
			locations = [locations]
		locations = ', '.join(locations)
		super(MULTIPLE_CHOICES, self).__init__(locations, *args, **kwargs)


class MOVED_PERMANENTLY(object):
	u"""The the server knows the target resource but the URI
		is incorrect (wrong domain, trailing slash, etc.).
		It can also be send if a resource have moved or
		renamed to prevent broken links."""
	__metaclass__ = StatusType
	code = 301


class FOUND(object):
	__metaclass__ = StatusType
	code = 302


class SEE_OTHER(object):
	u"""The request has been processed but instead of serving a
		representation of the result or resource it links to another
		document which contains a static status message, etc. so
		the client is not forced to download the data.
		This is also useful for links like
		/release-latest.tar.gz -> /release-1.2.tar.gz"""
	__metaclass__ = StatusType
	code = 303


class NOT_MODIFIED(object):
	u"""The client already has the data which is provided through the
		information in the Etag or If-Modified-Since-header.
		The Date-header is required, the ETag-header and
		Content-Location-header are useful.
		Also the caching headers Expires, Cache-Control and Vary are
		required if they differ from those sent previously.
		TODO: what to do if the representation format has
		changed but not the representation itself?
		The response body has to be empty."""
	__metaclass__ = StatusType
	code = 304
	body = None

	def __init__(self, *args, **kwargs):
		# don't set location
		HTTPStatusException.__init__(self, *args, **kwargs)

	header_to_remove = ("Allow", "Content-Encoding", "Content-Language",
						"Content-Length", "Content-MD5", "Content-Range",
						"Content-Type", "Expires", "Location")


class USE_PROXY(object):
	__metaclass__ = StatusType
	code = 305

# Unused, HTTP1.0
#SWITCH_PROXY = class (object):
#	__metaclass__ = StatusType
#	code = 306


class TEMPORARY_REDIRECT(object):
	u"""The request has not processed because the requested
		resource is located at a different URI.
		The client should resent the request to the URI given in the Location-header.
		for GET this is the same as 303 but for POST, PUT and DELETE it is
		important that the request was not processed."""
	__metaclass__ = StatusType
	code = 307

# Unused, HTTP1.0
#PERMANENT_REDIRECT = class (object):
#	__metaclass__ = StatusType
#	code = 308


class BAD_REQUEST(object):
	u"""The generic response code for client side errors.
		The response entity-body should contain information
		about what is wrong with the request."""
	__metaclass__ = StatusType
	code = 400


class UNAUTHORIZED(object):
	u"""The requested resource is protected and no or wrong
		authentication credentials were given.
		The WWW-Authenticate-header contains information about
		the accepted authentication method.
		The entity-body should contain information about what was wrong with
		the given credentials and where to register a new account.
	"""
	__metaclass__ = StatusType
	code = 401

	def __init__(self, authenticate, *args, **kwargs):
		kwargs.setdefault('headers', {})['WWW-Authenticate'] = authenticate
		super(UNAUTHORIZED, self).__init__(*args, **kwargs)

	def to_dict(self):
		dct = super(UNAUTHORIZED, self).to_dict()
		dct.update(dict({'WWW-Authenticate': self.headers['WWW-Authenticate']}))
		return dct


class PAYMENT_REQUIRED(object):
	__metaclass__ = StatusType
	code = 402
	# Reserved for future use


class FORBIDDEN(object):
	u"""The resource can only be served for specific users, at a specific time
		or from a certain IP address, etc."""
	__metaclass__ = StatusType
	code = 403


class NOT_FOUND(object):
	u"""No resource could be found at the given URI."""
	__metaclass__ = StatusType
	code = 404

	def __init__(self, path, **kwargs):
		self.path = path
		kwargs.update(dict(description='The requested resource "%s" was not found on this server.' % (path)))
		super(NOT_FOUND, self).__init__(**kwargs)


class METHOD_NOT_ALLOWED(object):
	u"""The client tried to use a HTTP Method which is not allowed.
		The Allow-header has to contain the allowed methods for this resource.
	"""
	__metaclass__ = StatusType
	code = 405

	def __init__(self, allow, *args, **kwargs):
		kwargs.setdefault('headers', {})['Allow'] = allow
		super(METHOD_NOT_ALLOWED, self).__init__(*args, **kwargs)

	def to_dict(self):
		dct = super(METHOD_NOT_ALLOWED, self).to_dict()
		dct.update(dict(Allow=self.headers['Allow']))
		return dct


class NOT_ACCEPTABLE(object):
	u"""The clients Accept-\*-header wants a representation of
		the resource which the server can not deliver.
		The entity body should contain a list of links with
		acceptable representations (similar to 300)."""
	__metaclass__ = StatusType
	code = 406


class PROXY_AUTHENTICATION_REQUIRED(object):
	__metaclass__ = StatusType
	code = 407


class REQUEST_TIMEOUT(object):
	u"""The client opens a connection to a server without sending a
		request after a specific amount of time."""
	__metaclass__ = StatusType
	code = 408


class CONFLICT(object):
	u"""If the request would cause to leave the resource in an inconsequent
		state this status is send.
		Examples: DELETE of a non empty bucket, changing a username to
		a already taken username.
		The location header can point to the conflicting resource.
		The entity body should contain a description of the conflict."""
	__metaclass__ = StatusType
	code = 409


class GONE(object):
	u"""The resource exists but is not anymore available (propably DELETEd)"""
	__metaclass__ = StatusType
	code = 410


class LENGTH_REQUIRED(object):
	u"""If a request representation is given but no Content-Length-header
		the HTTP server can decide to respond with this status code."""
	__metaclass__ = StatusType
	code = 411


class PRECONDITION_FAILED(object):
	u"""If a condition from any of the If-\*-headers except for conditional
		GET fails this status code is the respond."""
	__metaclass__ = StatusType
	code = 412


class REQUEST_ENTITY_TOO_LARGE(object):
	u"""The HTTP server can deny too large representations.
		A LBYL request can be useful.
		If the server can only not handle the request e.g. because of
		full disk space it can send the Retry-After-header."""
	__metaclass__ = StatusType
	code = 413


class REQUEST_URI_TOO_LONG(object):
	u"""Raised if the given URI is too long for the server."""
	__metaclass__ = StatusType
	code = 414


class UNSUPPORTED_MEDIA_TYPE(object):
	u"""This status code is sent when the server does not know
		the representation media type given in Content-Type-header.
		If the representation is just broken use 400 or 422."""
	__metaclass__ = StatusType
	code = 415


class REQUEST_RANGE_NOT_SATISFIABLE(object):
	__metaclass__ = StatusType
	code = 416


class EXPECTATION_FAILED(object):
	u"""This is the response code if a LBYL request (Expect-header) fails.
		It is the flip side of 100 Continue."""
	__metaclass__ = StatusType
	code = 417


class I_AM_A_TEAPOT(object):
	__metaclass__ = StatusType
	code = 418


#class ENHANCE_YOUR_CALM(object):
#	__metaclass__ = StatusType
#	code = 420


#class UNPROCESSABLE_ENTITY(object):
#	__metaclass__ = StatusType
#	code = 422


#class LOCKED(object):
#	__metaclass__ = StatusType
#	code = 423


#class FAILED_DEPENDENCY(object):
#	__metaclass__ = StatusType
#	code = 424


#class METHOD_FAILURE(object):
#	__metaclass__ = StatusType
#	code = 424


#class UNORDERED_COLLECTION(object):
#	__metaclass__ = StatusType
#	code = 425


#class UPGRADE_REQUIRED(object):
#	__metaclass__ = StatusType
#	code = 426


#class PRECONDITION_REQUIRED(object):
#	__metaclass__ = StatusType
#	code = 428


#class TOO_MANY_REQUESTS(object):
#	__metaclass__ = StatusType
#	code = 429


#class REQUEST_HEADER_FIELDS_TOO_LARGE(object):
#	__metaclass__ = StatusType
#	code = 431


#class NO_RESPONSE(object):
#	__metaclass__ = StatusType
#	code = 444


#class UNAVAILABLE_FOR_LEGAL_REASONS(object):
#	__metaclass__ = StatusType
#	code = 451


#class CLIENT_CLOSED_REQUEST(object):
#	__metaclass__ = StatusType
#	code = 499


class INTERNAL_SERVER_ERROR(object):
	u"""The generic status code.
		Mostly used when an exception in the request handler occurrs."""
	__metaclass__ = StatusType
	code = 500


class NOT_IMPLEMENTED(object):
	u"""The client tried to use a HTTP feature which the server does not support.
		Used if the server does not know the request method."""
	__metaclass__ = StatusType
	code = 501


class BAD_GATEWAY(object):
	u"""Problem with the proxy server."""
	__metaclass__ = StatusType
	code = 502


class SERVICE_UNAVAILABLE(object):
	u"""There is currently a problem with the server.
		Propably too many requests at once."""
	__metaclass__ = StatusType
	code = 503


class GATEWAY_TIMEOUT(object):
	u"""The proxy could not connect to the upstream server."""
	__metaclass__ = StatusType
	code = 504


class HTTP_VERSION_NOT_SUPPORTED(object):
	u"""The clients http version is not supported.
		This should not happen since HTTP 1.1 is backward compatible.
		The entity-body should contain a list of supported protocols."""
	__metaclass__ = StatusType
	code = 505

#class VARIANT_ALSO_NEGOTIATES(object):
#	__metaclass__ = StatusType
#	code = 506

#class INSUFFICIENT_STORAGE(object):
#	__metaclass__ = StatusType
#	code = 507

#class LOOP_DETECTED(object):
#	__metaclass__ = StatusType
#	code = 508

#class BANDWIDTH_LIMIT_EXCEEDET(object):
#	__metaclass__ = StatusType
#	code = 509

#class NOT_EXTENDED(object):
#	__metaclass__ = StatusType
#	code = 510

#class NETWORK_AUTHENTICATION_REQUIRED(object):
#	__metaclass__ = StatusType
#	code = 511

#class NETWORK_READ_TIMEOUT_ERROR(object):
#	__metaclass__ = StatusType
#	code = 598

#class NETWORK_CONNECT_TIMEOUT_ERROR(object):
#	__metaclass__ = StatusType
#	code = 599

for member in locals().copy().values():
	if isinstance(member, StatusType):
		STATUSES[member.status] = member
