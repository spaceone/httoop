"""
HTTPOOP - an OOP model of the HTTP protocol.

.. seealso:: :rfc:`2616`
"""

from httoop import cache
from httoop.client import ClientStateMachine
from httoop.date import Date
from httoop.exceptions import DecodeError, EncodeError, InvalidBody, InvalidDate, InvalidHeader, InvalidLine, InvalidURI
from httoop.header import Headers
from httoop.messages import Body, Method, Protocol, Request, Response
from httoop.proxy import ProxyStateMachine
from httoop.semantic import ComposedRequest, ComposedResponse
from httoop.server import ServerStateMachine
from httoop.status import (
    ACCEPTED,
    BAD_GATEWAY,
    BAD_REQUEST,
    CONFLICT,
    CONTENT_TOO_LARGE,
    CONTINUE,
    CREATED,
    EXPECTATION_FAILED,
    FORBIDDEN,
    FOUND,
    GATEWAY_TIMEOUT,
    GONE,
    HTTP_VERSION_NOT_SUPPORTED,
    I_AM_A_TEAPOT,
    INTERNAL_SERVER_ERROR,
    LENGTH_REQUIRED,
    METHOD_NOT_ALLOWED,
    MOVED_PERMANENTLY,
    MULTIPLE_CHOICES,
    NO_CONTENT,
    NON_AUTHORITATIVE_INFORMATION,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    NOT_IMPLEMENTED,
    NOT_MODIFIED,
    OK,
    PARTIAL_CONTENT,
    PAYMENT_REQUIRED,
    PRECONDITION_FAILED,
    PROXY_AUTHENTICATION_REQUIRED,
    RANGE_NOT_SATISFIABLE,
    REQUEST_TIMEOUT,
    RESET_CONTENT,
    SEE_OTHER,
    SERVICE_UNAVAILABLE,
    SWITCHING_PROTOCOLS,
    TEMPORARY_REDIRECT,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
    UNSUPPORTED_MEDIA_TYPE,
    URI_TOO_LONG,
    USE_PROXY,
    Status,
    StatusException,
)
from httoop.uri import URI
from httoop.version import ServerHeader, ServerProtocol, UserAgentHeader, __version__


__all__ = [
    'ACCEPTED', 'BAD_GATEWAY', 'BAD_REQUEST', 'CONFLICT', 'CONTINUE', 'CREATED', 'EXPECTATION_FAILED', 'FORBIDDEN', 'FOUND', 'GATEWAY_TIMEOUT',
    'GONE', 'HTTP_VERSION_NOT_SUPPORTED', 'INTERNAL_SERVER_ERROR', 'I_AM_A_TEAPOT', 'LENGTH_REQUIRED', 'METHOD_NOT_ALLOWED', 'MOVED_PERMANENTLY',
    'MULTIPLE_CHOICES', 'NON_AUTHORITATIVE_INFORMATION', 'NOT_ACCEPTABLE', 'NOT_FOUND', 'NOT_IMPLEMENTED', 'NOT_MODIFIED', 'NO_CONTENT', 'OK',
    'PARTIAL_CONTENT', 'CONTENT_TOO_LARGE', 'PAYMENT_REQUIRED', 'PRECONDITION_FAILED', 'PROXY_AUTHENTICATION_REQUIRED', 'RANGE_NOT_SATISFIABLE',
    'REQUEST_TIMEOUT', 'RESET_CONTENT', 'SEE_OTHER', 'SERVICE_UNAVAILABLE', 'SWITCHING_PROTOCOLS', 'TEMPORARY_REDIRECT', 'UNAUTHORIZED',
    'UNPROCESSABLE_ENTITY', 'UNSUPPORTED_MEDIA_TYPE', 'URI', 'URI_TOO_LONG', 'USE_PROXY',
    'Body', 'ClientStateMachine', 'ComposedRequest', 'ComposedResponse', 'Date', 'DecodeError', 'EncodeError', 'Headers',
    'InvalidBody', 'InvalidDate', 'InvalidHeader', 'InvalidLine', 'InvalidURI',
    'Method', 'Protocol', 'ProxyStateMachine', 'Request', 'Response', 'ServerHeader', 'ServerProtocol', 'ServerStateMachine', 'Status',
    'StatusException', 'UserAgentHeader', '__version__', 'cache',
]
