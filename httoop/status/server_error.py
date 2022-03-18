# -*- coding: utf-8 -*-

from httoop.status.types import StatusException


class ServerErrorStatus(StatusException):
	u"""SERVER_ERRORS = 5xx
		Indicates that something gone wrong on the server side.
		The server can send the Retry-After header if
		it knows that the problem is temporary.
	"""

	def to_dict(self):
		dct = super(ServerErrorStatus, self).to_dict()
		dct.update(dict(traceback=self.traceback or ""))
		return dct


class INTERNAL_SERVER_ERROR(ServerErrorStatus):
	u"""The generic status code.
		Mostly used when an exception in the request handler occurs."""

	code = 500
	cacheable = True


class NOT_IMPLEMENTED(ServerErrorStatus):
	u"""The client tried to use a HTTP feature which the server does not support.
		Used if the server does not know the request method."""

	code = 501


class BAD_GATEWAY(ServerErrorStatus):
	u"""Problem with the proxy server."""

	code = 502
	cacheable = True


class SERVICE_UNAVAILABLE(ServerErrorStatus):
	u"""There is currently a problem with the server.
		Probably too many requests at once."""

	code = 503
	cacheable = True


class GATEWAY_TIMEOUT(ServerErrorStatus):
	u"""The proxy could not connect to the upstream server."""

	code = 504
	cacheable = True


class HTTP_VERSION_NOT_SUPPORTED(ServerErrorStatus):
	u"""The clients http version is not supported.
		This should not happen since HTTP 1.1 is backward compatible.
		The entity-body should contain a list of supported protocols."""

	code = 505


class VARIANT_ALSO_NEGOTIATES(ServerErrorStatus):

	code = 506


class INSUFFICIENT_STORAGE(ServerErrorStatus):

	code = 507


class LOOP_DETECTED(ServerErrorStatus):

	code = 508


class BANDWIDTH_LIMIT_EXCEEDET(ServerErrorStatus):

	code = 509


#class NOT_EXTENDED(ServerErrorStatus):
#
#	code = 510


class NETWORK_AUTHENTICATION_REQUIRED(ServerErrorStatus):

	code = 511


#class NETWORK_READ_TIMEOUT_ERROR(ServerErrorStatus):
#
#	code = 598

#class NETWORK_CONNECT_TIMEOUT_ERROR(ServerErrorStatus):
#
#	code = 599
