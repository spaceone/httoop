import pytest


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


def test_if_match_header(headers):
    headers.parse(b'If-Match: W/"foo"')
    assert headers.element('If-Match') == 'W/"foo"'
    assert headers.element('If-Match').matches('W/"foo"')
    assert headers.element('If-Match') != '"foo"'
    assert headers.element('If-Match') != 'foo'
    assert headers.element('If-Match') != '*'
    assert headers.element('If-Match').matches_etag('foo', strong=False)
    assert not headers.element('If-Match').matches_etag('foo')


def test_if_match_header_star(headers):
    headers.parse(b'If-Match: *')
    assert headers.element('If-Match') == 'W/"foo"'


@pytest.mark.parametrize('match', [
    '"def456"',
    '"abc123", "def456", "ghi789"',
    '*',
])
def test_if_match_header_raw(headers, match):
    etag = 'def456'
    headers.parse(f'If-Match: {match}'.encode())
    assert any(condition.matches_etag(etag) for condition in headers.elements('If-Match'))


@pytest.mark.parametrize('match', [
    '"def456"',
    'W/"def456"',
    '"abc123", "def456", "ghi789"',
    '*',
])
def test_if_none_match_header_raw(headers, match):
    etag = 'def456'
    headers.parse(f'If-Match: {match}'.encode())
    assert any(condition.matches_etag(etag, strong=False) for condition in headers.elements('If-Match'))


@pytest.mark.parametrize('match', [
    'def456',
    'w/"def456"',
    'W/"def456"',
    '"abc123", "ghi789"',
])
def test_if_mismatch_header_raw(headers, match):
    etag = 'def456'
    headers.parse(f'If-Match: {match}'.encode())
    assert not any(condition.matches_etag(etag) for condition in headers.elements('If-Match'))
