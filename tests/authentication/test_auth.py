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
	(name, ''),
	(name, 'foobar'),
	(name, 'foobarbaz realm="test"'),
] for name in ('WWW-Authenticate', 'Authorization', 'Proxy-Authenticate', 'Proxy-Authorization'))))
def test_parse_invalid_header(name, invalid, headers):
	headers.parse('%s: %s' % (name, invalid))
	with pytest.raises(InvalidHeader):
		headers.element(name)

@pytest.mark.parametrize('clazz,value', [
	(WWWAuthenticate, ''),
	(WWWAuthenticate, 'foo'),
	(ProxyAuthenticate, ''),
	(ProxyAuthenticate, 'foo'),
	(Authorization, ''),
	(Authorization, 'foo'),
	(ProxyAuthorization, ''),
	(ProxyAuthorization, 'foo'),
])
def test_compose_invalid_header(clazz, value):
	h = clazz(value)
	with pytest.raises(InvalidHeader):
		bytes(h)
