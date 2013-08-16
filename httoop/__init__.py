# -*- coding: utf-8 -*-
"""HTTPOOP - an OOP model of the HTTP protocol

.. seealso:: :rfc:`2616`
"""

# TODO: PEP3101

__all__ = ['Status', 'Body', 'Headers', 'URI', 'Method',
           'Request', 'Response', 'Protocol', 'Date', 'StateMachine',
           'InvalidLine', 'InvalidHeader', 'InvalidURI', 'InvalidBody', 'InvalidDate',
           'CONTINUE', 'SWITCHING_PROTOCOLS', 'OK', 'CREATED', 'ACCEPTED', 'NON_AUTHORITATIVE_INFORMATION',
           'NO_CONTENT', 'RESET_CONTENT', 'PARTIAL_CONTENT', 'MULTIPLE_CHOICES', 'MOVED_PERMANENTLY', 'FOUND',
           'SEE_OTHER', 'NOT_MODIFIED', 'USE_PROXY', 'TEMPORARY_REDIRECT', 'BAD_REQUEST', 'UNAUTHORIZED', 'PAYMENT_REQUIRED',
           'FORBIDDEN', 'NOT_FOUND', 'METHOD_NOT_ALLOWED', 'NOT_ACCEPTABLE', 'PROXY_AUTHENTICATION_REQUIRED',
           'REQUEST_TIMEOUT', 'CONFLICT', 'GONE', 'LENGTH_REQUIRED', 'PRECONDITION_FAILED', 'REQUEST_ENTITY_TOO_LARGE',
           'REQUEST_URI_TOO_LONG', 'UNSUPPORTED_MEDIA_TYPE', 'REQUEST_RANGE_NOT_SATISFIABLE', 'EXPECTATION_FAILED',
           'I_AM_A_TEAPOT', 'INTERNAL_SERVER_ERROR', 'NOT_IMPLEMENTED', 'BAD_GATEWAY', 'SERVICE_UNAVAILABLE',
           'GATEWAY_TIMEOUT', 'HTTP_VERSION_NOT_SUPPORTED']
__version__ = 0.0

from httoop.status import Status
from httoop.date import Date
from httoop.headers import Headers
from httoop.body import Body
from httoop.uri import URI
from httoop.messages import Request, Response, Protocol, Method
from httoop.exceptions import InvalidLine, InvalidHeader, InvalidURI, InvalidBody, InvalidDate
from httoop.parser import StateMachine

from httoop.statuses import CONTINUE, SWITCHING_PROTOCOLS, OK, CREATED, ACCEPTED, NON_AUTHORITATIVE_INFORMATION
from httoop.statuses import NO_CONTENT, RESET_CONTENT, PARTIAL_CONTENT, MULTIPLE_CHOICES, MOVED_PERMANENTLY, FOUND
from httoop.statuses import SEE_OTHER, NOT_MODIFIED, USE_PROXY, TEMPORARY_REDIRECT, BAD_REQUEST, UNAUTHORIZED, PAYMENT_REQUIRED
from httoop.statuses import FORBIDDEN, NOT_FOUND, METHOD_NOT_ALLOWED, NOT_ACCEPTABLE, PROXY_AUTHENTICATION_REQUIRED
from httoop.statuses import REQUEST_TIMEOUT, CONFLICT, GONE, LENGTH_REQUIRED, PRECONDITION_FAILED, REQUEST_ENTITY_TOO_LARGE
from httoop.statuses import REQUEST_URI_TOO_LONG, UNSUPPORTED_MEDIA_TYPE, REQUEST_RANGE_NOT_SATISFIABLE, EXPECTATION_FAILED
from httoop.statuses import I_AM_A_TEAPOT, INTERNAL_SERVER_ERROR, NOT_IMPLEMENTED, BAD_GATEWAY, SERVICE_UNAVAILABLE
from httoop.statuses import GATEWAY_TIMEOUT, HTTP_VERSION_NOT_SUPPORTED
