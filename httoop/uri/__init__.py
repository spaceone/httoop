# -*- coding: utf-8 -*-
"""Uniform Resource Identifier

.. seealso:: :rfc:`3986`
"""

from httoop.uri.uri import URI
from httoop.uri.http import HTTP, HTTPS
from httoop.uri.schemes import GitSSH

__all__ = ('URI', 'HTTP', 'HTTPS', 'GitSSH')
