# -*- coding: utf-8 -*-
"""HTTP headers.

.. seealso:: :rfc:`2616#section-2.2`

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""

# FIXME: python3?
# TODO: add a MAXIMUM of 500 headers?

import inspect

from httoop.header import range  # pylint: disable=W0622
from httoop.header import auth, cache, conditional, messaging, security, semantics
from httoop.header.element import HEADER, HeaderElement, HeaderType
from httoop.header.headers import Headers
from httoop.header.messaging import Server, UserAgent

__all__ = ['Headers', 'Server', 'UserAgent']

types = (semantics, messaging, conditional, range, cache, auth, security)

for _, member in (member for type_ in types for member in inspect.getmembers(type_, inspect.isclass)):
	if isinstance(member, HeaderType) and member is not HeaderElement and not _.startswith('_'):
		HEADER[member.__name__] = member
		globals()[_] = member
		__all__.append(_)
