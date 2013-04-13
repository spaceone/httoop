# -*- coding: utf-8 -*-
"""HTTPOOP - an OOP model of the HTTP protocol

.. seealso:: :rfc:`2616`
"""

# comment about coding style:
# tabs for indentation because len('\t') == 1 and len('    ') == 4
# also max(len(line)) == 120 because we have 1920px width, we are not in year 1980 anymore
# if there are other PEP issues let me know!
# feedback (about anything or any line) is welcome!!

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
