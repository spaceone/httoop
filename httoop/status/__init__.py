# -*- coding: utf-8 -*-
"""HTTP status codes

.. seealso:: :rfc:`2616#section-6.2`
.. seealso:: :rfc:`2616#section-10`
"""

import inspect

__all__ = ['Status', 'REASONS', 'StatusType', 'StatusException']

from httoop.status.status import Status, REASONS
from httoop.status.types import StatusType, StatusException

from httoop.status import informational
from httoop.status import success
from httoop.status import redirect
from httoop.status import client_error
from httoop.status import server_error

# mapping of status -> Class
STATUSES = dict()
types = (informational, success, redirect, client_error, server_error)

for _, member in (member for type_ in types for member in inspect.getmembers(type_, inspect.isclass)):
	if isinstance(member, StatusType) and member is not StatusType:
		STATUSES[member.code] = member
		globals()[_] = member
		__all__.append(_)
