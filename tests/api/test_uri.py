def test_uri_set_string(request_):
	request_.uri = '/foo'
	assert request_.uri == '/foo'
