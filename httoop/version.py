# -*- coding: utf-8 -*-

__version__ = 0.0
from httoop.header import Server as __Server, UserAgent as __UserAgent
from httoop.messages import Protocol
UserAgentHeader = __UserAgent.parse('%s/%s' % (__name__, __version__))
ServerHeader = __Server.parse('%s/%s' % (__name__, __version__))
ServerProtocol = Protocol((1, 1))
