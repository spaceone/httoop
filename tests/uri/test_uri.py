from httoop import URI


def test_simple_uri_comparision(uri):
	u1 = URI(b'http://abc.com:80/~smith/home.html')
	u2 = URI(b'http://ABC.com/%7Esmith/home.html')
	u3 = URI(b'http://ABC.com:/%7esmith/home.html')
	u4 = URI(b'http://ABC.com:/%7esmith/./home.html')
	u5 = URI(b'http://ABC.com:/%7esmith/foo/../home.html')
	assert u1 == u2
	assert u2 == u3
	assert u1 == u3
	assert u1 == u4
	assert u1 == u5


def test_request_uri_maxlength():
	pass


def test_request_uri_is_star():
	pass


def test_request_uri_containig_fragment():
	pass


def test_invalid_uri_scheme():
	pass


def test_invalid_port():
	pass


def test_invalid_query_string():
	pass


def test_normalized_uri_redirects():
	pass
