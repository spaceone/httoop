from httoop.header import WWWAuthenticate, Authorization, Headers


def test_digest():
	www_auth = WWWAuthenticate('Digest', {
		'realm': 'testrealm@host.com',
		'qop': ['auth', 'auth-int'],
		'nonce': 'dcd98b7102dd2f0e8b11d0f600bfb0c093',
		'opaque': '5ccc069c403ebaf9f0171e9517f40e41'}
	)
	bytes(www_auth)
	www_auth_bytes = '''WWW-Authenticate: Digest realm="testrealm@host.com",
	nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
	opaque="5ccc069c403ebaf9f0171e9517f40e41",
	algorithm="MD5",
	qop="auth,auth-int"'''

	auth = Authorization('Digest', {
		'username': 'Mufasa',
		'realm': www_auth.params['realm'],
		'nonce': www_auth.params['nonce'],
		'uri': '/dir/index.html',
		'password':'Circle Of Life',
		'method': 'GET',
		'qop':'auth',
		'nc': '00000001',
		'cnonce': '0a4f113b',
		'opaque': www_auth.params['opaque']}
	)
	bytes(auth)
	auth_bytes = '''Authorization: Digest username="Mufasa",
	realm="testrealm@host.com",
	nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
	uri="/dir/index.html",
	response="6629fae49393a05397450978507c4ef1",
	cnonce="0a4f113b",
	opaque="5ccc069c403ebaf9f0171e9517f40e41",
	qop="auth",
	nc="00000001"'''
	return  # TODO: parse() not yet implemented
	h = Headers()
	h.parse(auth_bytes)
	assert auth == h.elements('Authorization')[0]
	h.parse(www_auth_bytes)
	assert www_auth == h.elements('WWW-Authenticate')[0]
