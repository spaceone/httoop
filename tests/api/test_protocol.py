def test_protocol_tuple(request):
	request.protocol.parse(b'HTTP/1.0')
	assert request.protocol == (1, 0)


def test_set_protocol_tuple(request):
	request.protocol = (1, 0)
	assert bytes(request.protocol) == b'HTTP/1.0'


def test_protocol_minor_mayor(request):
	request.protocol = (1, 0)
	assert request.protocol.major == 1
	assert request.protocol.minor == 0


def test_protocol_compare_bytes(request):
	request.protocol = (1, 0)
	assert request.protocol == b'HTTP/1.0'


def test_set_protocol_to_protocol(request, response):
	request.protocol = (1, 0)
	response.protocol = request.protocol
	assert response.protocol == (1, 0)


def test_protocol_comparision(request):
	request.protocol = (1, 2)
	assert request.protocol < (2, 0)
	assert request.protocol < 2
	assert request.protocol > (0, 9)
	assert request.protocol > 0
	assert request.protocol < (1, 3)
	assert request.protocol > (1, 0)
	assert request.protocol == (1, 2)
	assert request.protocol != (2, 0)
	assert request.protocol == 1
	assert request.protocol != 0
	assert request.protocol != 2
	assert request.protocol != 'foo'
	assert request.protocol >= (1, 2)
	assert request.protocol >= (1, 1)
	assert request.protocol <= (1, 2)
	assert request.protocol <= (2, 1)
	assert not (request.protocol != 1)
