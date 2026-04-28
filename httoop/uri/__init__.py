"""
Uniform Resource Identifier.

.. seealso:: :rfc:`3986`
"""

import httoop.uri.schemes  # noqa: F401
from httoop.uri.http import HTTP, HTTPS
from httoop.uri.uri import URI


__all__ = ('HTTP', 'HTTPS', 'URI')
