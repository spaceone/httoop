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
