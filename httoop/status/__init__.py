# -*- coding: utf-8 -*-
"""HTTP status codes.

.. seealso:: :rfc:`2616#section-6.2`
.. seealso:: :rfc:`2616#section-10`
"""

import inspect

from httoop.status import client_error, informational, redirect, server_error, success
from httoop.status.status import REASONS, Status
from httoop.status.types import StatusException, StatusType

__all__ = ['Status', 'REASONS', 'StatusType', 'StatusException']

# mapping of status -> Class
STATUSES = dict()
types = (informational, success, redirect, client_error, server_error)

for _, member in (member for type_ in types for member in inspect.getmembers(type_, inspect.isclass)):
	if isinstance(member, StatusType) and member is not StatusType:
		STATUSES[member.code] = member
		globals()[_] = member
		__all__.append(_)
