# -*- coding: utf-8 -*-

from httoop.status.types import StatusType


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
