# -*- coding: utf-8 -*-
"""HTTPOOP - an OOP model of the HTTP protocol.

.. seealso:: :rfc:`2616`
"""

from __future__ import absolute_import

from httoop import cache
from httoop.client import ClientStateMachine
from httoop.date import Date
from httoop.exceptions import (
	DecodeError, EncodeError, InvalidBody, InvalidDate, InvalidHeader, InvalidLine, InvalidURI,
)
from httoop.header import Headers
from httoop.messages import Body, Method, Protocol, Request, Response
from httoop.proxy import ProxyStateMachine
from httoop.semantic import ComposedRequest, ComposedResponse
from httoop.server import ServerStateMachine
from httoop.status import (
	ACCEPTED, BAD_GATEWAY, BAD_REQUEST, CONFLICT, CONTINUE, CREATED, EXPECTATION_FAILED, FORBIDDEN, FOUND,
	GATEWAY_TIMEOUT, GONE, HTTP_VERSION_NOT_SUPPORTED, I_AM_A_TEAPOT, INTERNAL_SERVER_ERROR,
	LENGTH_REQUIRED, METHOD_NOT_ALLOWED, MOVED_PERMANENTLY, MULTIPLE_CHOICES, NO_CONTENT,
	NON_AUTHORITATIVE_INFORMATION, NOT_ACCEPTABLE, NOT_FOUND, NOT_IMPLEMENTED, NOT_MODIFIED, OK,
	PARTIAL_CONTENT, PAYLOAD_TOO_LARGE, PAYMENT_REQUIRED, PRECONDITION_FAILED,
	PROXY_AUTHENTICATION_REQUIRED, RANGE_NOT_SATISFIABLE, REQUEST_TIMEOUT, RESET_CONTENT, SEE_OTHER,
	SERVICE_UNAVAILABLE, SWITCHING_PROTOCOLS, TEMPORARY_REDIRECT, UNAUTHORIZED, UNPROCESSABLE_ENTITY,
	UNSUPPORTED_MEDIA_TYPE, URI_TOO_LONG, USE_PROXY, Status, StatusException,
)
from httoop.uri import URI
from httoop.version import ServerHeader, ServerProtocol, UserAgentHeader, __version__

__all__ = [
	'Status', 'Body', 'Headers', 'URI', 'Method',
	'Request', 'Response', 'Protocol', 'Date', 'ServerStateMachine', 'ClientStateMachine',
	'ProxyStateMachine', 'InvalidLine', 'InvalidHeader', 'InvalidURI', 'InvalidBody', 'InvalidDate',
	'CONTINUE', 'SWITCHING_PROTOCOLS', 'OK', 'CREATED', 'ACCEPTED',
	'NON_AUTHORITATIVE_INFORMATION', 'NO_CONTENT', 'RESET_CONTENT',
	'PARTIAL_CONTENT', 'MULTIPLE_CHOICES', 'MOVED_PERMANENTLY', 'FOUND',
	'SEE_OTHER', 'NOT_MODIFIED', 'USE_PROXY', 'TEMPORARY_REDIRECT',
	'BAD_REQUEST', 'UNAUTHORIZED', 'PAYMENT_REQUIRED', 'FORBIDDEN',
	'NOT_FOUND', 'METHOD_NOT_ALLOWED', 'NOT_ACCEPTABLE', 'GONE',
	'PROXY_AUTHENTICATION_REQUIRED', 'REQUEST_TIMEOUT', 'CONFLICT',
	'LENGTH_REQUIRED', 'PRECONDITION_FAILED', 'PAYLOAD_TOO_LARGE',
	'URI_TOO_LONG', 'UNSUPPORTED_MEDIA_TYPE', 'BAD_GATEWAY',
	'RANGE_NOT_SATISFIABLE', 'EXPECTATION_FAILED',
	'I_AM_A_TEAPOT', 'INTERNAL_SERVER_ERROR', 'NOT_IMPLEMENTED',
	'SERVICE_UNAVAILABLE', 'GATEWAY_TIMEOUT', 'UNPROCESSABLE_ENTITY',
	'HTTP_VERSION_NOT_SUPPORTED', 'StatusException',
	'DecodeError', 'EncodeError',
	'__version__', 'ServerProtocol', 'UserAgentHeader', 'ServerHeader',
	'cache', 'ComposedRequest', 'ComposedResponse',
]

try:
	__import__('pkg_resources').declare_namespace(__name__)
except ImportError:  # pragma: no cover
	__path___ = __import__('pkgutil').extend_path(__path__, __name__)
