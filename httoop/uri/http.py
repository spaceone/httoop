"""
HTTP URLs
.. seealso:: :rfc:`2616#section-3.2`.

.. seealso:: :rfc:`2616#section-3.2.2`
"""

from httoop.uri.uri import URI


class HTTP(URI, scheme='http'):
    __slots__ = ()
    PORT = 80


class HTTPS(HTTP, scheme='https'):
    __slots__ = ()
    PORT = 443
