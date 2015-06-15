def test_request_syntax_basic(request):
	request.uri = '/'
	request.method = 'GET'
	request.protocol = (1, 1)
	assert bytes(request) == b'GET / HTTP/1.1\r\n'

def test_response_syntax_basic(response):
	response.status = 200
	response.protocol = (1, 1)
	assert bytes(response) == b'HTTP/1.1 200 OK\r\n'
