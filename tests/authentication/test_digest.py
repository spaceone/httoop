# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest

from itertools import product, chain

from httoop.header import WWWAuthenticate, Authorization
from httoop.exceptions import InvalidHeader


def test_digest_www_authentication(headers):
	www_auth = WWWAuthenticate('Digest', {
		'realm': 'testrealm@host.com',
		'qop': ['auth', 'auth-int'],
		'nonce': 'dcd98b7102dd2f0e8b11d0f600bfb0c093',
		'opaque': '5ccc069c403ebaf9f0171e9517f40e41'}
	)
	www_auth = WWWAuthenticate.parse(bytes(www_auth))
	www_auth_bytes = b'''WWW-Authenticate: Digest realm="testrealm@host.com",
	nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
	opaque="5ccc069c403ebaf9f0171e9517f40e41",
	algorithm="MD5",
	qop="auth,auth-int"'''
	headers.parse(www_auth_bytes)
	assert www_auth.params == headers.elements('WWW-Authenticate')[0].params


def test_digest_authorization(headers):
	auth = Authorization('Digest', {
		'username': 'Mufasa',
		'realm': 'testrealm@host.com',
		'nonce': 'dcd98b7102dd2f0e8b11d0f600bfb0c093',
		'uri': '/dir/index.html',
		'password': 'Circle Of Life',
		'method': 'GET',
		'qop': 'auth',
		'nc': '00000001',
		'cnonce': '0a4f113b',
		'opaque': '5ccc069c403ebaf9f0171e9517f40e41'}
	)
	auth = Authorization.parse(bytes(auth))
	auth_bytes = b'''Authorization: Digest username="Mufasa",
	realm="testrealm@host.com",
	nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
	uri="/dir/index.html",
	response="6629fae49393a05397450978507c4ef1",
	cnonce="0a4f113b",
	opaque="5ccc069c403ebaf9f0171e9517f40e41",
	qop="auth",
	nc="00000001"'''
	headers.parse(auth_bytes)
	assert auth.params == headers.element('Authorization').params


def test_unknown_algorithm(headers):
	auth = Authorization('Digest', {
		'algorithm': 'bar', 'username': 'foo', 'realm': 'foo',
		'uri': '/'
	})
	with pytest.raises(InvalidHeader) as excinfo:
		bytes(auth)
	assert 'algorithm' in str(excinfo)


required = ('algorithm', 'username', 'realm', 'uri')


@pytest.mark.parametrize('params', set(tuple(tuple(set(x)) for x in chain(*list(set(product(required, repeat=i)) for i in range(1, len(required) + 1))))))
def test_required_parameter(params, headers):
	pvars = {
		b'algorithm': b'MD5',
		b'username': b'foo',
		b'realm': b'foo',
		b'uri': b'/'
	}
	header = b', '.join(b'%s="%s"' % (p, pvars[p]) for p in params)
	headers.parse(b'Authorization: digest %s' % header)
	with pytest.raises(InvalidHeader) as excinfo:
		headers.elements('Authorization')
	assert 'Missing parameter' in str(excinfo)

	element = Authorization(u'Digest', dict((p, pvars[p].decode('ascii')) for p in params))
	with pytest.raises(InvalidHeader) as excinfo:
		bytes(element)
	assert 'Missing parameter' in str(excinfo)
