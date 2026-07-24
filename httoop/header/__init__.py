"""
HTTP headers.

.. seealso:: :rfc:`2616#section-2.2`

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""

from httoop.header import auth, cache, conditional, messaging, ranges, security
from httoop.header.element import HEADER, HeaderElement
from httoop.header.headers import Headers
from httoop.header.messaging import Server, UserAgent


__all__ = ['HeaderElement', 'Headers', 'Server', 'UserAgent', 'auth', 'cache', 'conditional', 'messaging', 'ranges', 'security']
for member in HEADER.values():
    name = member.__name__
    __all__ += name  # noqa: PLE0605
    globals()[name] = member
