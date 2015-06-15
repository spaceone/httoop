def test_uri_set_string(request):
	request.uri = '/foo'
	assert request.uri == '/foo'
