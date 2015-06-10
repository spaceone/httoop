from httoop.header import WWWAuthenticate, Authorization, Headers


def test_basic_www_authenticate():
	www_auth = WWWAuthenticate('Basic', {'realm': 'simple'})
	auth = Authorization('Basic', {'username': 'admin', 'password': '12345'})
	assert bytes(www_auth) in ('Basic realm="simple"', 'Basic realm=simple')
	assert bytes(auth) == 'Basic YWRtaW46MTIzNDU='
	h = Headers()
	h.parse('WWW-Authenticate: %s' % www_auth)
	h.parse('Authorization: %s' % auth)
	assert h.elements('WWW-Authenticate')[0].realm == u'simple'
	assert h.element('Authorization').params['username'] == u'admin'
	assert h.element('Authorization').params['password'] == u'12345'
