# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from httoop.exceptions import InvalidHeader
from httoop.header import Authorization, WWWAuthenticate


def test_basic_www_authenticate(headers):
	www_auth = WWWAuthenticate('Basic', {'realm': 'simple'})
	assert bytes(www_auth) in (b'Basic realm="simple"', b'Basic realm=simple')
	headers.parse(b'WWW-Authenticate: %s' % www_auth)
	assert headers.elements('WWW-Authenticate')[0].realm == u'simple'


def test_basic_authorization(headers):
	auth = Authorization('Basic', {'username': 'admin', 'password': '12345'})
	assert bytes(auth) == b'Basic YWRtaW46MTIzNDU='
	headers.parse(b'Authorization: %s' % auth)
	assert headers.element('Authorization').params['username'] == b'admin'
	assert headers.element('Authorization').params['password'] == b'12345'


@pytest.mark.parametrize('invalid', (b'foo', b'Zm9v', u'föo'.encode('latin1')))
def test_invalid_headers(headers, invalid):
	headers.parse(b'Authorization: Basic %s' % (invalid,))
	with pytest.raises(InvalidHeader):
		headers.element('Authorization')
	headers.clear()
