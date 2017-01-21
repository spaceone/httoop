# -*- coding: utf-8 -*-

from __future__ import absolute_import

__version__ = 0.0
from httoop.header import Server as __Server, UserAgent as __UserAgent
from httoop.messages import Protocol
UserAgentHeader = __UserAgent.parse(b'httoop/%.1f' % (__version__,))
ServerHeader = __Server.parse(b'httoop/%.1f' % (__version__,))
ServerProtocol = Protocol((1, 1))
