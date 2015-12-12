from httoop import URI


def test_scheme_difference():
	assert URI(b'http://foo.example:1/') != URI(b'ftp://foo.example:1/')
	assert URI(b'http://foo.example:1/') != b'ftp://foo.example:1'
	assert URI(b'ftp://foo.example:1/') != b'http://foo.example:1'
