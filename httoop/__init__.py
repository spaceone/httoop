# -*- coding: utf-8 -*-
"""HTTPOOP - an OOP model of the HTTP protocol

.. seealso:: :rfc:`2616`
"""

# TODO: PEP3101

__all__ = ['Status', 'Body', 'Headers', 'URI', 'Method'
           'Request', 'Response', 'Protocol', 'Date',
           'InvalidLine', 'InvalidHeader', 'InvalidURI']
__version__ = 0.0

from httoop.status import Status
from httoop.date import Date
from httoop.headers import Headers
from httoop.body import Body
from httoop.uri import URI
from httoop.messages import Request, Response, Protocol, Method
from httoop.exceptions import InvalidLine, InvalidHeader, InvalidURI
from httoop.parser import StateMachine
