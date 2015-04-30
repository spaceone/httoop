# -*- coding: utf-8 -*-

from httoop.status.types import StatusType


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
