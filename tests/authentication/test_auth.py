from __future__ import unicode_literals
import pytest
from itertools import chain
from httoop.header import WWWAuthenticate, Authorization, ProxyAuthenticate, ProxyAuthorization
from httoop.exceptions import InvalidHeader


@pytest.mark.parametrize('scheme', ['Basic', 'Digest'])
def test_realm_replaces_quote(scheme):
	w = WWWAuthenticate(scheme)
	w.realm = u'My "Realm"'
	assert w.realm == u'My Realm'


@pytest.mark.parametrize('name,invalid', chain(*([
	(name, b''),
	(name, b'foobar'),
	(name, b'foobarbaz realm="test"'),
] for name in (b'WWW-Authenticate', b'Authorization', b'Proxy-Authenticate', b'Proxy-Authorization'))))
def test_parse_invalid_header(name, invalid, headers):
	headers.parse(b'%s: %s' % (name, invalid))
	with pytest.raises(InvalidHeader):
		headers.element(name)


@pytest.mark.parametrize('clazz,value', [
	(WWWAuthenticate, u''),
	(WWWAuthenticate, u'foo'),
	(ProxyAuthenticate, u''),
	(ProxyAuthenticate, u'foo'),
	(Authorization, u''),
	(Authorization, u'foo'),
	(ProxyAuthorization, u''),
	(ProxyAuthorization, u'foo'),
])
def test_compose_invalid_header(clazz, value):
	h = clazz(value)
	with pytest.raises(InvalidHeader):
		bytes(h)


def test_order(headers):
	headers.parse(b'WWW-Authenticate: basic realm="foo"')
	headers.parse(b'WWW-Authenticate: digest realm="bar", nonce=foo, opaque=foo, algorithm=MD5, qop=auth')
	assert headers.elements(u'WWW-Authenticate') == [u'Digest', u'Basic']
