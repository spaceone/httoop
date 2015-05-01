# -*- coding: utf-8 -*-
"""HTTP headers

.. seealso:: :rfc:`2616#section-2.2`

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""

__all__ = ['Headers']

# FIXME: python3?
# TODO: add a MAXIMUM of 500 headers?

import inspect

from httoop.header.element import HEADER, HeaderElement, HeaderType
from httoop.header.messaging import Server, UserAgent
from httoop.header.headers import Headers

from httoop.header import semantics
from httoop.header import messaging
from httoop.header import conditional
from httoop.header import range
from httoop.header import cache
from httoop.header import auth

types = (semantics, messaging, conditional, range, cache, auth)

for _, member in (member for type_ in types for member in inspect.getmembers(type_, inspect.isclass)):
	if isinstance(member, HeaderType) and member is not HeaderElement:
		HEADER[member.__name__] = member
