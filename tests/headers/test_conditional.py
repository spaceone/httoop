def test_conditional_header(headers):
	headers.parse(b'Last-Modified: Mon, 15 Jun 2020 21:18:41 GMT')
	headers.parse(b'If-Modified-Since: Mon, 15 Jun 2020 21:18:40 GMT')
	headers.parse(b'If-Unmodified-Since: Mon, 15 Jun 2020 21:18:42 GMT')
	lm = headers.element('Last-Modified')
	im = headers.element('If-Modified-Since')
	iu = headers.element('If-Unmodified-Since')
	assert iu > lm > im
	assert im < lm < iu
	assert im != lm != iu
	assert im != 'foo'


def test_etag_header(headers):
	headers.parse(b'ETag: foo')
	assert headers.element('ETag') == 'foo'
	assert headers.element('ETag') == '*'
	assert headers.element('ETag') != 'bar'
