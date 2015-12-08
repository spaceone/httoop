# -*- coding: utf-8 -*-
"""Uniform Resource Identifier

.. seealso:: :rfc:`3986`
"""

__all__ = ('URI', 'HTTP', 'HTTPS')

from httoop.uri.uri import URI
from httoop.uri.http import HTTP, HTTPS
import httoop.uri.schemes
