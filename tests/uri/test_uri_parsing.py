
import pytest

from httoop import URI, InvalidURI


absolute_uris = [
    (b'http://localhost:8090/foo/bar/?x=y#blub', ('http', '', '', 'localhost', 8090, '/foo/bar/', 'x=y', 'blub')),
    (b'http://localhost:8090/foo/bar/?x=y#blub', ('http', '', '', 'localhost', 8090, '/foo/bar/', 'x=y', 'blub')),
    (b'http://a:b@c:8090/d/?e=f#g', ('http', 'a', 'b', 'c', 8090, '/d/', 'e=f', 'g')),
    (b'http://www.python.org', ('http', '', '', 'www.python.org', 80, '', '', '')),
    (b'http://www.python.org#abc', ('http', '', '', 'www.python.org', 80, '', '', 'abc')),
    (b'http://www.python.org?q=abc', ('http', '', '', 'www.python.org', 80, '', 'q=abc', '')),
    (b'http://www.python.org/#abc', ('http', '', '', 'www.python.org', 80, '/', '', 'abc')),
    (b'http://a/b/c/d;p?q#f', ('http', '', '', 'a', 80, '/b/c/d;p', 'q', 'f')),
    (b'https://www.python.org', ('https', '', '', 'www.python.org', 443, '', '', '')),
    (b'https://www.python.org#abc', ('https', '', '', 'www.python.org', 443, '', '', 'abc')),
    (b'https://www.python.org?q=abc', ('https', '', '', 'www.python.org', 443, '', 'q=abc', '')),
    (b'https://www.python.org/#abc', ('https', '', '', 'www.python.org', 443, '/', '', 'abc')),
    (b'https://a/b/c/d;p?q#f', ('https', '', '', 'a', 443, '/b/c/d;p', 'q', 'f')),

    (b'sip:alice@atlanta.com;maddr=239.255.255.1;ttl=15', ('sip', '', '', '', None, 'alice@atlanta.com;maddr=239.255.255.1;ttl=15', '', '')),  # RFC 3261
    (b'http://example.com?blahblah=/foo', ('http', '', '', 'example.com', 80, '', 'blahblah=/foo', '')),

    (b'eXAMPLE://a/./b/../b/%63/%7bfoo%7d', ('example', '', '', 'a', None, '/./b/../b/c/{foo}', '', '')),
    (b'example://a/b/c/%7Bfoo%7D', ('example', '', '', 'a', None, '/b/c/{foo}', '', '')),

    (b'http', ('', '', '', '', None, 'http', '', '')),
    (b'http:example:', ('http', '', '', '', 80, 'example:', '', '')),
    (b'http:example', ('http', '', '', '', 80, 'example', '', '')),
    (b'http:example:90', ('http', '', '', '', 80, 'example:90', '', '')),
    (b'http://example:/', ('http', '', '', 'example', 80, '/', '', '')),
    (b'path', ('', '', '', '', None, 'path', '', '')),
    (b'path:', ('path', '', '', '', None, '', '', '')),
    (b'path%3a', ('', '', '', '', None, 'path:', '', '')),
    (b'//www.python.org:80', ('', '', '', 'www.python.org', 80, '', '', '')),
    (b'http://www.python.org:80', ('http', '', '', 'www.python.org', 80, '', '', '')),

    (b'mailto:1337@example.org', ('mailto', '', '', '', None, '1337@example.org', '', '')),
    (b's3://foo.com/stuff', ('s3', '', '', 'foo.com', None, '/stuff', '', '')),
    (b'x-newscheme://foo.com/stuff', ('x-newscheme', '', '', 'foo.com', None, '/stuff', '', '')),
    (b'x-newscheme://foo.com/stuff?query#fragment', ('x-newscheme', '', '', 'foo.com', None, '/stuff', 'query', 'fragment')),
    (b'x-newscheme://foo.com/stuff?query', ('x-newscheme', '', '', 'foo.com', None, '/stuff', 'query', '')),

    (b'tel:+31-641044153', ('tel', '', '', '', None, '+31-641044153', '', '')),

    (b'http:', ('http', '', '', '', 80, '', '', '')),
    (b'ftp:', ('ftp', '', '', '', 21, '', '', '')),
    (b'https:', ('https', '', '', '', 443, '', '', '')),
    (b'http://', ('http', '', '', '', 80, '', '', '')),
    (b'ftp://', ('ftp', '', '', '', 21, '', '', '')),
    (b'https://', ('https', '', '', '', 443, '', '', '')),

    # python's urlparse makes the following invalid parsing. should we do the same? better not...
    # pytest.param((b'int:80', (u'', u'', u'', u'', None, u'int:80', u'', u'')), marks=pytest.mark.xfail),
    (b'int:80', ('int', '', '', '', None, '80', '', '')),

    (b'http://good.com@evil.com:8090/foo?bar=baz', ('http', 'good.com', '', 'evil.com', 8090, '/foo', 'bar=baz', '')),
    (b'http://good.com/@evil.com:8090/foo?bar=baz', ('http', '', '', 'good.com', 80, '/@evil.com:8090/foo', 'bar=baz', '')),

    (b'http://example.com:443', ('http', '', '', 'example.com', 443, '', '', '')),
    (b'https://example.com:80', ('https', '', '', 'example.com', 80, '', '', '')),
    (b'http://www.example.com:65535', ('http', '', '', 'www.example.com', 65535, '', '', '')),
    (b'http://www.example.com:1', ('http', '', '', 'www.example.com', 1, '', '', '')),

    (b'http:#foo', ('http', '', '', '', 80, '', '', 'foo')),
    (b'http://#foo', ('http', '', '', '', 80, '', '', 'foo')),
    (b'http://#a?b', ('http', '', '', '', 80, '', '', 'a?b')),
    (b'http:///foo:bar@baz:80/test', ('http', '', '', '', 80, '/foo:bar@baz:80/test', '', '')),
    (b'http://..', ('http', '', '', '..', 80, '', '', '')),
    (b'http:///..', ('http', '', '', '', 80, '/..', '', '')),
    (b'http://.', ('http', '', '', '.', 80, '', '', '')),
    (b'http:///.', ('http', '', '', '', 80, '/.', '', '')),
    (b'http:.', ('http', '', '', '', 80, '.', '', '')),
    (b'http:..', ('http', '', '', '', 80, '..', '', '')),
    (b'http:/', ('http', '', '', '', 80, '/', '', '')),
    (b'http://foo/bar.', ('http', '', '', 'foo', 80, '/bar.', '', '')),

    (b'foo:bar', ('foo', '', '', '', None, 'bar', '', '')),
    (b'foo%3Abar', ('', '', '', '', None, 'foo:bar', '', '')),
    (b'md5:61529519452809720693702583126814', ('md5', '', '', '', None, '61529519452809720693702583126814', '', '')),
    (b'md5:acbd18db4cc2f85cedef654fccc4a4d8', ('md5', '', '', '', None, 'acbd18db4cc2f85cedef654fccc4a4d8', '', '')),

    (b'http://localhost:8090/foo/bar/?x=b%3Da%26r', ('http', '', '', 'localhost', 8090, '/foo/bar/', 'x=b%3Da%26r', '')),
]
# absolute_uris.extend(
#    (b'http://www.example.com:%d' % (port,), (u'http', u'', u'', u'www.example.com', port, u'', u'', u'')) for port in range(1, 65535)
# )


@pytest.mark.parametrize('url,expected', absolute_uris)
def test_parse_absolute_uri(url, expected):
    uri = URI()
    uri.parse(url)
    assert uri.tuple == expected


@pytest.mark.parametrize('url', [
    # Invalid IPv6 Addresses
    b'http://::12.34.56.78]/',
    b'http://[::1/foo/',
    b'ftp://[::1/foo/bad]/bad',
    b'http://[::1/foo/bad]/bad',
    b'http://[::ffff:12.34.56.78',
    b'http://]dead:beef::1[:5432/foo/',
    b'http://][dead:beef::1][:5432/foo/',
    b'http://[[dead:beef::1]]:5432/foo/',
    b'http://dead:beef::1]:5432/foo/',
    b'http://dead:beef::1]/foo/',
    b'http://[dead:beef::1:5432/foo/',
    b'http://[dead:beef::1/foo/',
    # invalid IPv4 Addresses
    b'http://1.2.3.256/',
    pytest.param(b'http://1.2.-3.4/', marks=pytest.mark.xfail),
    b'http://1.2.03.4/',
    # invalid Ports
    b'http://www.example.net:foo',
    b'http://www.example.net:-123',
    b'http://www.example.net:65536',
    b'http://www.example.net:0',
    # Invalid IPvFuture
    b'http://[v123.deaf:bee\xff]/',
    # Invalid host
    b'http://www.ex%c3%a4mple.net',
    pytest.param(b'http://www.ex%e4mple.net', marks=pytest.mark.xfail()),
])
def test_parse_invalid_netloc(url):
    with pytest.raises(InvalidURI):
        URI(url)


@pytest.mark.parametrize('u', [b'Python', b'./Python', b'x-newscheme://foo.com/stuff', b'x://y', b'x:/y', b'x:/', b'/', ])
def test_unparse_parse(u):
    assert bytes(URI(u)) == u


@pytest.mark.parametrize('url,hostname,port', [
    (b'http://Test.python.org:5432/foo/', 'test.python.org', 5432),
    (b'http://12.34.56.78:5432/foo/', '12.34.56.78', 5432),
    (b'http://[::1]:5432/foo/', '::1', 5432),
    (b'http://[dead:beef::1]:5432/foo/', 'dead:beef::1', 5432),
    (b'http://[dead:beef::]:5432/foo/', 'dead:beef::', 5432),
    (b'http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]:5432/foo/', 'dead:beef:cafe:5417:affe:8fa3:deaf:feed', 5432),
    (b'http://[::12.34.56.78]:5432/foo/', '::12.34.56.78', 5432),
    (b'http://[::ffff:12.34.56.78]:5432/foo/', '::ffff:12.34.56.78', 5432),
    (b'http://Test.python.org/foo/', 'test.python.org', 80),
    (b'http://12.34.56.78/foo/', '12.34.56.78', 80),
    (b'http://[::1]/foo/', '::1', 80),
    (b'http://[dead:beef::1]/foo/', 'dead:beef::1', 80),
    (b'http://[dead:beef::]/foo/', 'dead:beef::', 80),
    (b'http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]/foo/', 'dead:beef:cafe:5417:affe:8fa3:deaf:feed', 80),
    (b'http://[::12.34.56.78]/foo/', '::12.34.56.78', 80),
    (b'http://[::ffff:12.34.56.78]/foo/', '::ffff:12.34.56.78', 80),
    (b'http://Test.python.org:/foo/', 'test.python.org', 80),
    (b'http://12.34.56.78:/foo/', '12.34.56.78', 80),
    (b'http://[::1]:/foo/', '::1', 80),
    (b'http://[dead:beef::1]:/foo/', 'dead:beef::1', 80),
    (b'http://[dead:beef::]:/foo/', 'dead:beef::', 80),
    (b'http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]:/foo/', 'dead:beef:cafe:5417:affe:8fa3:deaf:feed', 80),
    (b'http://[::12.34.56.78]:/foo/', '::12.34.56.78', 80),
    (b'http://[::ffff:12.34.56.78]:/foo/', '::ffff:12.34.56.78', 80),
])
def test_rfc2732(url, hostname, port):
    url = URI(url)
    assert url.hostname == hostname
    assert url.port == port


@pytest.mark.parametrize('url,hostname,port', [
    (b'http://[v123.:]/', ':', 80),
    (b'http://[v123.dead:beef]/', 'dead:beef', 80),
    (b'http://[v0.dead:beef]/', 'dead:beef', 80),
    (b'http://[v0.foo:123]/', 'foo:123', 80),
    (b'http://[v123.:]:1/', ':', 1),
    (b'http://[v123.dead:beef]:2/', 'dead:beef', 2),
    (b'http://[v0.dead:beef]:3/', 'dead:beef', 3),
    (b'http://[v0.foo:123]:4/', 'foo:123', 4),
    (b'http://[v0.fo[]o:123]:4/', 'fo[]o:123', 4),
])
def test_ipvfuture(url, hostname, port):
    url = URI(url)
    assert url.hostname == hostname


def test_invalid_idna_uri():
    pass


@pytest.mark.parametrize('char', [
    b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07', b'\x08', b'\t', b'\n', b'\x0b', b'\x0c', b'\r', b'\x0e', b'\x0f', b'\x10', b'\x11', b'\x12', b'\x13', b'\x14', b'\x15', b'\x16', b'\x17', b'\x18', b'\x19', b'\x1a', b'\x1b', b'\x1c', b'\x1d', b'\x1e', b'\x1f', b' ', b'\xff'
])
def test_invalid_uri_characters(char):
    with pytest.raises(InvalidURI) as exc:
        URI().parse(b'/foo%sbar' % (char,))
    assert 'must consist of printable ASCII characters without whitespace.' in str(exc.value)


@pytest.mark.parametrize('char', [
    # b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07', b'\x08', b'\t', b'\n', b'\x0b', b'\x0c', b'\r', b'\x0e', b'\x0f', b'\x10', b'\x11', b'\x12', b'\x13', b'\x14', b'\x15', b'\x16', b'\x17', b'\x18', b'\x19', b'\x1a', b'\x1b', b'\x1c', b'\x1d', b'\x1e', b'\x1f', b' ',
    b'!', b'"', b'$', b'%', b'&', b"'", b'(', b')', b'*', b',', b'/', b':', b';', b'<', b'=', b'>', b'@', b'[', b'\\', b']', b'^', b'_', b'`', b'{', b'|', b'}', b'~',
])
def test_invalid_uri_scheme_characters(char):
    with pytest.raises(InvalidURI) as exc:
        URI().parse(b'ht%sp://example.com/' % (char,))
    assert 'must only contain alphanumeric letters or plus, dash, dot.' in str(exc.value)
