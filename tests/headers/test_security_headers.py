

def test_content_security_policy(headers):
	headers.parse(b"Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; object-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'; media-src 'self'; frame-src 'self'; font-src 'none'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; report-uri /csp-violation;")
	assert bytes(headers.get_element('Content-Security-Policy', 'media-src')) == b"media-src 'self'; "


def test_content_security_policy_element(headers):  # TODO(FIXME: very bad API design
	headers.append_element('Content-Security-Policy', u'default-src', {b"'self'": None})
	headers.append_element('Content-Security-Policy', u'font-src', {b"'none'": None})
	assert bytes(headers) == b"Content-Security-Policy: default-src 'self'; , font-src 'none'; \r\n\r\n"
