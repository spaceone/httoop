# -*- coding: utf-8 -*-

from __future__ import absolute_import

if __import__('sys').version_info < (3, 5) and __import__('sys').version_info > (2, 8):  # pragma: no cover
	raise RuntimeError('httoop only supports >= python2.7 and >= python3.5!')

from httoop.header import Server as __Server, UserAgent as __UserAgent  # noqa
from httoop.messages import Protocol  # noqa

__version__ = 0.0
UserAgentHeader = __UserAgent.parse('httoop/%.1f' % (__version__,))
ServerHeader = __Server.parse('httoop/%.1f' % (__version__,))
ServerProtocol = Protocol((1, 1))
