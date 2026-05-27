from __future__ import annotations

from hashlib import md5, new, sha256
from hmac import compare_digest
from time import time
from typing import Callable
from uuid import uuid4

from httoop.exceptions import InvalidHeader
from httoop.header.element import HeaderElement
from httoop.util import ByteUnicodeDict, _


class DigestAuthScheme:
    algorithms = {
        'MD5': lambda: md5(),  # noqa: S324
        'MD5-sess': lambda: md5(),  # noqa: S324
        'SHA-256': lambda: sha256(),
        'SHA-256-sess': lambda: sha256(),
        'SHA-512-256': lambda: new('sha512_256'),
        'SHA-512-256-sess': lambda: new('sha512_256'),
    }  # not case insensitive per RFC

    allowed_algorithms = frozenset(algorithms)
    qops = (b'auth', b'auth-int')  # quality of protection

    @classmethod
    def get_algorithm(cls, algorithm: bytes | str) -> Callable[[bytes], bytes]:
        if not isinstance(algorithm, str):
            algorithm = algorithm.decode('ASCII')

        if algorithm not in cls.allowed_algorithms:
            raise InvalidHeader(_('Digest algorithm not allowed: %r'), algorithm)

        try:
            H = cls.algorithms[algorithm]
        except KeyError:
            raise InvalidHeader(_('Unknown digest authentication algorithm: %r'), algorithm) from None

        def _algo(value: bytes) -> bytes:
            h = H()
            h.update(value)
            return h.hexdigest().encode('ASCII')

        return _algo

    @classmethod
    def generate_nonce(cls, authinfo: ByteUnicodeDict) -> bytes:
        nonce = b'%d:%s:%s' % (
            time(),
            authinfo.get('etag', authinfo.get('realm', b'')),
            str(uuid4()).encode('ASCII'),
        )
        algorithm = authinfo.get('algorithm', b'MD5').decode('ASCII', 'replace')
        H = cls.get_algorithm(algorithm)
        return H(nonce)

    @classmethod
    def compose(cls, authinfo: ByteUnicodeDict) -> bytes:
        params = cls._compose(authinfo)
        return b', '.join([HeaderElement.formatparam(k.encode('ASCII'), v) for k, v in params])

    @classmethod
    def _compose(cls, authinfo):  # pragma: no cover
        return authinfo

    @classmethod
    def parse(cls, authinfo: bytes) -> ByteUnicodeDict:
        atoms = [x.strip() for x in authinfo.split(b',') if x.strip()] or [b'']

        params = {key.strip(): value.strip().strip(b'"') for key, _, value in (atom.partition(b'=') for atom in atoms)}
        return ByteUnicodeDict(params)


class DigestAuthResponseScheme(DigestAuthScheme):  # WWW-Authenticate

    @classmethod
    def _compose(cls, authinfo: ByteUnicodeDict) -> list[tuple[str, bytes]]:
        realm = authinfo['realm']
        algorithm = authinfo.get('algorithm', b'MD5')
        domain = authinfo.get('domain')
        if isinstance(domain, (list, tuple)):
            domain = b' '.join(domain)
        nonce = authinfo['nonce'].replace(b'"', b'')

        stale = authinfo.get('stale')
        if isinstance(stale, bool):
            stale = b'true' if stale else b'false'

        qop_options = authinfo.get('qop', tuple(cls.qops))
        if isinstance(qop_options, (list, tuple)):
            qop_options = b','.join(qop_options)

        params = [
            ('realm', realm),
            ('domain', domain),
            ('nonce', nonce),
            ('opaque', authinfo.get('opaque')),
            ('stale', stale),
            ('algorithm', algorithm),
            ('qop', qop_options),
            authinfo.get('auth-param', [None, None]),
        ]
        return [(k, v) for k, v in params if v is not None]

    @classmethod
    def parse(cls, authinfo: bytes) -> dict[str, bytes | list[bytes] | bool]:
        params = super(cls, cls).parse(authinfo)
        if b'"' in params['nonce']:
            raise InvalidHeader(_('Nonce must not contain double quote'))
        stale = params.get('stale')
        if stale:
            stale = {b'false': False, b'true': True}.get(stale.lower())
        params = [
            ('realm', params['realm']),
            ('domain', params.get('domain', b'').split()),
            ('nonce', params['nonce']),
            ('opaque', params.get('opaque')),
            ('stale', stale),
            ('algorithm', params.get('algorithm')),
            ('qop', [p.strip() for p in params.get('qop', b'').split(b',')]),
        ]
        return {k: v for k, v in params if v is not None}


class DigestAuthRequestScheme(DigestAuthScheme):  # Authorization

    @classmethod
    def _compose(cls, authinfo: ByteUnicodeDict) -> list[tuple[str, bytes]]:
        username = authinfo['username']
        realm = authinfo['realm']
        digest_uri = authinfo['uri']
        nonce = authinfo.get('nonce', b'').replace(b'"', b'')
        response = authinfo.get('response')
        cnonce = None
        nonce_count = None
        message_qop = authinfo.get('qop')
        if message_qop:
            cnonce = authinfo['cnonce']
            nonce_count = authinfo['nc']

        params = [
            ('username', username),
            ('realm', realm),
            ('nonce', nonce or cls.generate_nonce(authinfo)),
            ('uri', digest_uri),
            ('response', response or cls.calculate_request_digest(authinfo)),
            ('algorithm', authinfo.get('algorithm')),
            ('cnonce', cnonce),
            ('opaque', authinfo.get('opaque')),
            ('qop', message_qop),
            ('nc', nonce_count),
            authinfo.get('auth-param', [None, None]),
        ]
        return [(k, v) for k, v in params if v is not None]

    @classmethod
    def parse(cls, authinfo: bytes) -> dict[str, bytes]:
        params = super(cls, cls).parse(authinfo)
        message_qop = params.get('qop')
        cnonce = None
        nonce_count = None
        if message_qop:
            cnonce = params['cnonce']
            nonce_count = params['nc']
        params = [
            ('username', params['username']),
            ('realm', params['realm']),
            ('nonce', params['nonce']),
            ('uri', params['uri']),
            ('response', params['response']),
            ('algorithm', params.get('algorithm')),
            ('cnonce', cnonce),
            ('opaque', params.get('opaque')),
            ('qop', message_qop),
            ('nc', nonce_count),
        ]
        return {k: v for k, v in params if v is not None}

    @classmethod
    def check(cls, authinfo: ByteUnicodeDict, request_params: ByteUnicodeDict) -> bool:
        if authinfo['realm'] != request_params['realm']:
            return False
        response = cls.calculate_request_digest(authinfo)
        return len(response) == len(request_params['response']) and compare_digest(response, request_params['response'])

    @classmethod
    def calculate_request_digest(cls, authinfo: ByteUnicodeDict) -> bytes:
        algorithm = authinfo.get('algorithm', b'MD5').decode('ASCII', 'replace')
        H = cls.get_algorithm(algorithm)

        if algorithm.endswith('-sess') and authinfo.get('A1'):  # noqa: SIM108
            secret = H(authinfo['A1'])
        else:
            secret = H(cls.A1(authinfo))

        qop = authinfo.get('qop')
        hash_a2 = H(cls.A2(authinfo))
        if qop in {b'auth', b'auth-int'}:
            data = b'%s:%s:%s:%s:%s' % (authinfo['nonce'], authinfo['nc'], authinfo['cnonce'], authinfo['qop'], hash_a2)
        elif qop is None:
            data = b'%s:%s' % (authinfo['nonce'], hash_a2)
        else:  # pragma: no cover
            raise NotImplementedError(f'Unknown quality of protection: {qop!r}')

        return H(b'%s:%s' % (secret, data))

    @classmethod
    def A2(cls, params: ByteUnicodeDict) -> bytes:
        qop = params.get('qop', b'')
        if not qop or qop == b'auth':
            return b'%s:%s' % (params['method'], params['uri'])
        if qop == b'auth-int':
            H = cls.get_algorithm(params.get('algorithm', b'MD5'))
            return b'%s:%s:%s' % (params['method'], params['uri'], H(params['entity_body']))
        raise NotImplementedError(f'Unknown quality of protection: {qop!r}')  # pragma: no cover

    @classmethod
    def A1(cls, params: ByteUnicodeDict) -> bytes:
        algorithm = params.get('algorithm', b'')

        if not algorithm or not algorithm.endswith(b'-sess'):
            return b'%s:%s:%s' % (params['username'], params['realm'], params['password'])

        H = cls.get_algorithm(algorithm)
        s = b'%s:%s:%s' % (params['username'], params['realm'], params['password'])
        return b'%s:%s:%s' % (H(s), params['nonce'], params['cnonce'])


class SecureDigestAuthRequestScheme(DigestAuthRequestScheme):
    allowed_algorithms = frozenset({
        'SHA-256',
        'SHA-256-sess',
        'SHA-512-256',
        'SHA-512-256-sess',
    })
