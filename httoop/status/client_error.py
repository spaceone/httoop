# -*- coding: utf-8 -*-

from httoop.status.types import StatusException


class ClientErrorStatus(StatusException):
	u"""CLIENT_ERRORS = 4xx
		Something is wrong with the client: e.g. authentication,
		format of wanted representation, or error in the clients http library.
	"""

	pass


class BAD_REQUEST(ClientErrorStatus):
	u"""The generic response code for client side errors.
		The response entity-body should contain information
		about what is wrong with the request."""

	code = 400


class UNAUTHORIZED(ClientErrorStatus):
	u"""The requested resource is protected and no or wrong
		authentication credentials were given.
		The WWW-Authenticate-header contains information about
		the accepted authentication method.
		The entity-body should contain information about what was wrong with
		the given credentials and where to register a new account.
	"""

	code = 401

	def __init__(self, authenticate, *args, **kwargs):
		kwargs.setdefault('headers', {})['WWW-Authenticate'] = authenticate
		super(UNAUTHORIZED, self).__init__(*args, **kwargs)

	def to_dict(self):
		dct = super(UNAUTHORIZED, self).to_dict()
		dct.update(dict({'WWW-Authenticate': self.headers['WWW-Authenticate']}))
		return dct


class PAYMENT_REQUIRED(ClientErrorStatus):

	code = 402


class FORBIDDEN(ClientErrorStatus):
	u"""The resource can only be served for specific users, at a specific time
		or from a certain IP address, etc."""

	code = 403


class NOT_FOUND(ClientErrorStatus):
	u"""No resource could be found at the given URI."""

	code = 404

	def __init__(self, path, **kwargs):
		self.path = path
		kwargs.update(dict(description='The requested resource "%s" was not found on this server.' % (path,)))
		super(NOT_FOUND, self).__init__(**kwargs)


class METHOD_NOT_ALLOWED(ClientErrorStatus):
	u"""The client tried to use a HTTP Method which is not allowed.
		The Allow-header has to contain the allowed methods for this resource.
	"""

	code = 405

	def __init__(self, allow, *args, **kwargs):
		kwargs.setdefault('headers', {})['Allow'] = allow
		super(METHOD_NOT_ALLOWED, self).__init__(*args, **kwargs)

	def to_dict(self):
		dct = super(METHOD_NOT_ALLOWED, self).to_dict()
		dct.update(dict(Allow=self.headers['Allow']))
		return dct


class NOT_ACCEPTABLE(ClientErrorStatus):
	r"""The clients Accept-\*-header wants a representation of
		the resource which the server can not deliver.
		The entity body should contain a list of links with
		acceptable representations (similar to 300)."""

	code = 406


class PROXY_AUTHENTICATION_REQUIRED(ClientErrorStatus):

	code = 407


class REQUEST_TIMEOUT(ClientErrorStatus):
	u"""The client opens a connection to a server without sending a
		request after a specific amount of time."""

	code = 408

	def __init__(self, *args, **kwargs):
		kwargs.setdefault('headers', {})['Connection'] = 'close'
		super(REQUEST_TIMEOUT, self).__init__(*args, **kwargs)


class CONFLICT(ClientErrorStatus):
	u"""If the request would cause to leave the resource in an inconsequent
		state this status is send.
		Examples: DELETE of a non empty bucket, changing a username to
		a already taken username.
		The location header can point to the conflicting resource.
		The entity body should contain a description of the conflict."""

	code = 409


class GONE(ClientErrorStatus):
	u"""The resource exists but is not anymore available (propably DELETEd)"""

	code = 410


class LENGTH_REQUIRED(ClientErrorStatus):
	u"""If a request representation is given but no Content-Length-header
		the HTTP server can decide to respond with this status code."""

	code = 411


class PRECONDITION_FAILED(ClientErrorStatus):
	r"""If a condition from any of the If-\*-headers except for conditional
		GET fails this status code is the respond."""

	code = 412


class PAYLOAD_TOO_LARGE(ClientErrorStatus):
	u"""The HTTP server can deny too large representations.
		A LBYL request can be useful.
		If the server can only not handle the request e.g. because of
		full disk space it can send the Retry-After-header."""

	code = 413


class URI_TOO_LONG(ClientErrorStatus):
	u"""Raised if the given URI is too long for the server."""

	code = 414


class UNSUPPORTED_MEDIA_TYPE(ClientErrorStatus):
	u"""This status code is sent when the server does not know
		the representation media type given in Content-Type-header.
		If the representation is just broken use 400 or 422."""

	code = 415


class RANGE_NOT_SATISFIABLE(ClientErrorStatus):

	code = 416


class EXPECTATION_FAILED(ClientErrorStatus):
	u"""This is the response code if a LBYL request (Expect-header) fails.
		It is the flip side of 100 Continue."""

	code = 417


class I_AM_A_TEAPOT(ClientErrorStatus):

	code = 418


#class ENHANCE_YOUR_CALM(ClientErrorStatus):
#
#	code = 420


class MISDIRECTED_REQUEST(ClientErrorStatus):

	code = 421


class UNPROCESSABLE_ENTITY(ClientErrorStatus):

	code = 422


class LOCKED(ClientErrorStatus):

	code = 423


class FAILED_DEPENDENCY(ClientErrorStatus):

	code = 424


class UPGRADE_REQUIRED(ClientErrorStatus):

	code = 426

	def __init__(self, upgrade, *args, **kwargs):
		kwargs.setdefault('headers', {})['Upgrade'] = upgrade
		kwargs['headers']['Connection'] = 'Upgrade'
		super(UPGRADE_REQUIRED, self).__init__(*args, **kwargs)


class PRECONDITION_REQUIRED(ClientErrorStatus):

	code = 428


class TOO_MANY_REQUESTS(ClientErrorStatus):

	code = 429


class REQUEST_HEADER_FIELDS_TOO_LARGE(ClientErrorStatus):

	code = 431


#class NO_RESPONSE(ClientErrorStatus):
#
#	code = 444


#class UNAVAILABLE_FOR_LEGAL_REASONS(ClientErrorStatus):
#
#	code = 451


#class CLIENT_CLOSED_REQUEST(ClientErrorStatus):
#
#	code = 499
