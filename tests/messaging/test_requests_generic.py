def test_request_without_carriage_return_newlines():
	pass


def test_request_without_carriage_return_newlines_and_chunked_request_body():
	pass


def test_invalid_http_semantic():
	pass


def test_request_date():
	pass


def test_invalid_request_date():
	pass


def test_compose_empty_uri(request_):
	request_.uri.parse(b'')
	request_.parse(bytes(request_))
