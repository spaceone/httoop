# -*- coding: utf-8 -*-
import pytest

from httoop.header import WWWAuthenticate, Authorization
from httoop.exceptions import InvalidHeader


def test_basic_www_authenticate(headers):
	www_auth = WWWAuthenticate('Basic', {'realm': 'simple'})
	assert bytes(www_auth) in ('Basic realm="simple"', 'Basic realm=simple')
	headers.parse('WWW-Authenticate: %s' % www_auth)
	assert headers.elements('WWW-Authenticate')[0].realm == u'simple'


def test_basic_authorization(headers):
	auth = Authorization('Basic', {'username': 'admin', 'password': '12345'})
	assert bytes(auth) == 'Basic YWRtaW46MTIzNDU='
	headers.parse('Authorization: %s' % auth)
	assert headers.element('Authorization').params['username'] == u'admin'
	assert headers.element('Authorization').params['password'] == u'12345'

@pytest.mark.parametrize('invalid', (b'foo', b'Zm9v', u'föo'.encode('latin1')))
def test_invalid_headers(headers, invalid):
	headers.parse(b'Authorization: Basic %s' % (invalid,))
	with pytest.raises(InvalidHeader):
		headers.element('Authorization')
	headers.clear()
