from httoop import Headers


def test_merging_header(headers):
	h2 = Headers()
	headers['Host'] = 'localhost'
	h2['Host'] = 'localhost'
	headers['Accept'] = 'text/plain; q=1.6, text/html; q=0.3'
	h2['Accept'] = 'application/json; q=0.4'
	h2['Foo'] = 'bar'
	headers.merge(h2)
	assert set(headers.keys()) == set(['Host', 'Accept', 'Foo'])
	assert headers['Host'] == 'localhost, localhost'
	assert headers['Accept'] == 'text/plain; q=1.6, application/json; q=0.4, text/html; q=0.3'
	assert headers['Foo'] == 'bar'


def test_replace_headers(request_):
	request_.headers['A'] = 'a'
	request_.headers['B'] = 'B'
	request_.headers['C'] = 'c'
	request_.headers = {'D': 'D', 'E': 'e'}
	assert set(request_.headers.keys()) == {'D', 'E'}
	assert request_.headers['D'] == 'D'
	assert request_.headers['E'] == 'e'


def test_trailer(request_):
	request_.headers['A'] = 'a'
	request_.headers['B'] = 'B'
	request_.headers['C'] = 'c'
	request_.headers['D'] = 'D'
	request_.headers['E'] = 'e'
	request_.headers['Trailer'] = 'B, C, E, F'
	assert set(request_.trailer.keys()) == {'B', 'C', 'E'}
	assert request_.trailer['B'] == 'B'
	assert request_.trailer['C'] == 'c'
	assert request_.trailer['E'] == 'e'
