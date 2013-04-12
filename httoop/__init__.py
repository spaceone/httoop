# -*- coding: utf-8 -*-
"""HTTPOOP - an OOP model of the HTTP protocol

.. seealso:: :rfc:`2616`
"""

# tabs for indentation because len('\t') == 1 and len('    ') == 4
# also max(len(line)) == 120 because we have 1920px width, this is not 1980
# if there are other PEP issues let me know!
# also please tell me if this is bullshit or useful

__all__ = ['Status', 'Body', 'Headers', 'URI',
           'Request', 'Response', 'Protocol', 'Date',
           'InvalidLine', 'InvalidHeader', 'InvalidURI']
__version__ = 0.0

from httoop.status import Status
from httoop.date import Date
from httoop.headers import Headers
from httoop.body import Body
from httoop.uri import URI
from httoop.messages import Request, Response, Protocol
from httoop.exceptions import InvalidLine, InvalidHeader, InvalidURI
