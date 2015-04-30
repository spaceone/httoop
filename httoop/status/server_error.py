# -*- coding: utf-8 -*-

from httoop.status.types import StatusType


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
