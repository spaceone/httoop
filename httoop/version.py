from httoop.header import Server as __Server, UserAgent as __UserAgent
from httoop.messages import Protocol


__version__ = '0.1.1'
UserAgentHeader = __UserAgent.parse(b'httoop/%s' % (__version__.encode(), ))
ServerHeader = __Server.parse(b'httoop/%s' % (__version__.encode(), ))
ServerProtocol = Protocol((1, 1))
