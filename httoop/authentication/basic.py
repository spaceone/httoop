from __future__ import annotations

from httoop.exceptions import InvalidHeader
from httoop.header.element import HeaderElement
from httoop.util import Base64Error, ByteUnicodeDict, _, base64, base64_decode


class BasicAuthRequestScheme:

    @staticmethod
    def parse(authinfo: bytes) -> dict[str, bytes]:
        # try:
        #    authinfo = authinfo.encode('ascii')
        # except ValueError:
        #    raise InvalidHeader(_(u'Invalid base64 in basic authentication'))

        try:
            username, password = base64_decode(authinfo.strip()).split(b':', 1)
            if not username:
                raise ValueError()
        except Base64Error:
            raise InvalidHeader(_('Basic authentication contains invalid base64'))
        except ValueError:
            raise InvalidHeader(_('No username:password provided'))

        return {
            # 'username': username.decode('ISO8859-1'),
            # 'password': password.decode('ISO8859-1')
            'username': username,
            'password': password,
        }

    @staticmethod
    def compose(authinfo: ByteUnicodeDict) -> bytes:
        username = authinfo['username']
        password = authinfo['password']
        # username = username.encode('ISO8859-1')
        # password = password.encode('ISO8859-1')
        return base64(b'%s:%s' % (username, password))


class BasicAuthResponseScheme:

    @staticmethod
    def parse(authinfo: bytes) -> dict[bytes, str | bytes]:
        params = HeaderElement.parseparams(b'X;%s' % authinfo)[1]
        params.setdefault(b'realm', b'')
        return params

    @staticmethod
    def compose(authinfo: ByteUnicodeDict) -> bytes:
        return HeaderElement.formatparam(b'realm', authinfo['realm'], True)
