def test_request_syntax_basic(request_):
	request_.uri = '/'
	request_.method = 'GET'
	request_.protocol = (1, 1)
	assert bytes(request_) == b'GET / HTTP/1.1\r\n'

def test_response_syntax_basic(response):
	response.status = 200
	response.protocol = (1, 1)
	assert bytes(response) == b'HTTP/1.1 200 OK\r\n'
