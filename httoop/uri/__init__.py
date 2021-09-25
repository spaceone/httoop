# -*- coding: utf-8 -*-
"""Uniform Resource Identifier

.. seealso:: :rfc:`3986`
"""

from httoop.uri.http import HTTP, HTTPS
from httoop.uri.schemes import GitSSH
from httoop.uri.uri import URI

__all__ = ('URI', 'HTTP', 'HTTPS', 'GitSSH')
