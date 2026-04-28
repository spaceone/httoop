"""
HTTP status codes.

.. seealso:: :rfc:`2616#section-6.2`
.. seealso:: :rfc:`2616#section-10`
"""

from httoop.status.client_error import ClientErrorStatus
from httoop.status.informational import InformationalStatus
from httoop.status.redirect import RedirectStatus
from httoop.status.server_error import ServerErrorStatus
from httoop.status.status import REASONS, STATUSES, Status
from httoop.status.success import SuccessStatus
from httoop.status.types import StatusException


__all__ = ['REASONS', 'ClientErrorStatus', 'InformationalStatus', 'RedirectStatus', 'ServerErrorStatus', 'Status', 'StatusException', 'SuccessStatus']

for member in STATUSES.values():
    __all__.append(member.__name__)
    globals()[member.__name__] = member
