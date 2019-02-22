import pytest
from httoop import URI, InvalidURI

absolute_uris = [
	(b'http://localhost:8090/foo/bar/?x=y#blub', (u'http', u'', u'', u'localhost', 8090, u'/foo/bar/', u'x=y', u'blub')),
	(b'http://localhost:8090/foo/bar/?x=y#blub', (u'http', u'', u'', u'localhost', 8090, u'/foo/bar/', u'x=y', u'blub')),
	(b'http://a:b@c:8090/d/?e=f#g', (u'http', u'a', u'b', u'c', 8090, u'/d/', u'e=f', u'g')),
	(b'http://www.python.org', (u'http', u'', u'', 'www.python.org', 80, '', '', '')),
	(b'http://www.python.org#abc', (u'http', u'', u'', 'www.python.org', 80, '', '', 'abc')),
	(b'http://www.python.org?q=abc', (u'http', u'', u'', 'www.python.org', 80, '', 'q=abc', '')),
	(b'http://www.python.org/#abc', (u'http', u'', u'', 'www.python.org', 80, '/', '', 'abc')),
	(b'http://a/b/c/d;p?q#f', (u'http', u'', u'', 'a', 80, '/b/c/d;p', 'q', 'f')),
	(b'https://www.python.org', (u'https', u'', u'', 'www.python.org', 443, '', '', '')),
	(b'https://www.python.org#abc', (u'https', u'', u'', 'www.python.org', 443, '', '', 'abc')),
	(b'https://www.python.org?q=abc', (u'https', u'', u'', 'www.python.org', 443, '', 'q=abc', '')),
	(b'https://www.python.org/#abc', (u'https', u'', u'', 'www.python.org', 443, '/', '', 'abc')),
	(b'https://a/b/c/d;p?q#f', (u'https', u'', u'', 'a', 443, '/b/c/d;p', 'q', 'f')),

	(b'sip:alice@atlanta.com;maddr=239.255.255.1;ttl=15', (u'sip', u'', u'', u'', None, u'alice@atlanta.com;maddr=239.255.255.1;ttl=15', u'', u'')),  # RFC 3261
	(b'http://example.com?blahblah=/foo', (u'http', u'', u'', u'example.com', 80, u'', u'blahblah=/foo', u'')),

	(b'eXAMPLE://a/./b/../b/%63/%7bfoo%7d', (u'example', u'', u'', u'a', None, u'/./b/../b/c/{foo}', u'', u'')),
	(b'example://a/b/c/%7Bfoo%7D', (u'example', u'', u'', u'a', None, u'/b/c/{foo}', u'', u'')),

	(b'http', (u'', u'', u'', u'', None, u'http', u'', u'')),
	(b'http:example:', (u'http', u'', u'', u'', 80, u'example:', u'', u'')),
	(b'http:example', (u'http', u'', u'', u'', 80, u'example', u'', u'')),
	(b'http:example:90', (u'http', u'', u'', u'', 80, u'example:90', u'', u'')),
	(b'http://example:/', (u'http', u'', u'', u'example', 80, u'/', u'', u'')),
	(b'path', (u'', u'', u'', u'', None, u'path', u'', u'')),
	(b'path:', (u'path', u'', u'', u'', None, u'', u'', u'')),
	(b'path%3a', (u'', u'', u'', u'', None, u'path:', u'', u'')),
	(b'//www.python.org:80', (u'', u'', u'', u'www.python.org', 80, u'', u'', u'')),
	(b'http://www.python.org:80', (u'http', u'', u'', u'www.python.org', 80, u'', u'', u'')),

	(b'mailto:1337@example.org', (u'mailto', u'', u'', u'', None, u'1337@example.org', u'', u'')),
	(b"s3://foo.com/stuff", (u's3', u'', u'', u'foo.com', None, u'/stuff', u'', u'')),
	(b"x-newscheme://foo.com/stuff", (u'x-newscheme', u'', u'', u'foo.com', None, u'/stuff', u'', u'')),
	(b"x-newscheme://foo.com/stuff?query#fragment", (u'x-newscheme', u'', u'', u'foo.com', None, u'/stuff', u'query', u'fragment')),
	(b"x-newscheme://foo.com/stuff?query", (u'x-newscheme', u'', u'', u'foo.com', None, u'/stuff', u'query', u'')),

	(b'tel:+31-641044153', (u'tel', u'', u'', u'', None, u'+31-641044153', u'', u'')),

	(b'http:', (u'http', u'', u'', u'', 80, u'', u'', u'')),
	(b'ftp:', (u'ftp', u'', u'', u'', 21, u'', u'', u'')),
	(b'https:', (u'https', u'', u'', u'', 443, u'', u'', u'')),
	(b'http://', (u'http', u'', u'', u'', 80, u'', u'', u'')),
	(b'ftp://', (u'ftp', u'', u'', u'', 21, u'', u'', u'')),
	(b'https://', (u'https', u'', u'', u'', 443, u'', u'', u'')),

	# python's urlparse makes the following invalid parsing. should we do the same? better not...
	# pytest.param((b'int:80', (u'', u'', u'', u'', None, u'int:80', u'', u'')), marks=pytest.mark.xfail),
	(b'int:80', (u'int', u'', u'', u'', None, u'80', u'', u'')),

	(b'http://good.com@evil.com:8090/foo?bar=baz', (u'http', u'good.com', u'', u'evil.com', 8090, u'/foo', u'bar=baz', u'')),
	(b'http://good.com/@evil.com:8090/foo?bar=baz', (u'http', u'', u'', u'good.com', 80, u'/@evil.com:8090/foo', u'bar=baz', u'')),

	(b'http://example.com:443', (u'http', u'', u'', u'example.com', 443, u'', u'', u'')),
	(b'https://example.com:80', (u'https', u'', u'', u'example.com', 80, u'', u'', u'')),
	(b'http://www.example.com:65535', (u'http', u'', u'', u'www.example.com', 65535, u'', u'', u'')),
	(b'http://www.example.com:1', (u'http', u'', u'', u'www.example.com', 1, u'', u'', u'')),

	(b'http:#foo', (u'http', u'', u'', u'', 80, u'', u'', u'foo')),
	(b'http://#foo', (u'http', u'', u'', u'', 80, u'', u'', u'foo')),
	(b'http://#a?b', (u'http', u'', u'', u'', 80, u'', u'', u'a?b')),
	(b'http:///foo:bar@baz:80/test', (u'http', u'', u'', u'', 80, u'/foo:bar@baz:80/test', u'', u'')),
	(b'http://..', (u'http', u'', u'', u'..', 80, u'', u'', u'')),
	(b'http:///..', (u'http', u'', u'', u'', 80, u'/..', u'', u'')),
	(b'http://.', (u'http', u'', u'', u'.', 80, u'', u'', u'')),
	(b'http:///.', (u'http', u'', u'', u'', 80, u'/.', u'', u'')),
	(b'http:.', (u'http', u'', u'', u'', 80, u'.', u'', u'')),
	(b'http:..', (u'http', u'', u'', u'', 80, u'..', u'', u'')),
	(b'http:/', (u'http', u'', u'', u'', 80, u'/', u'', u'')),
	(b'http://foo/bar.', (u'http', u'', u'', u'foo', 80, u'/bar.', u'', u'')),

	(b'foo:bar', (u'foo', u'', u'', u'', None, u'bar', u'', u'')),
	(b'foo%3Abar', (u'', u'', u'', u'', None, u'foo:bar', u'', u'')),
	(b'md5:61529519452809720693702583126814', (u'md5', u'', u'', u'', None, u'61529519452809720693702583126814', u'', u'')),
	(b'md5:acbd18db4cc2f85cedef654fccc4a4d8', (u'md5', u'', u'', u'', None, u'acbd18db4cc2f85cedef654fccc4a4d8', u'', u'')),
]
#absolute_uris.extend(
#	(b'http://www.example.com:%d' % (port,), (u'http', u'', u'', u'www.example.com', port, u'', u'', u'')) for port in range(1, 65535)
#)


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
])
def test_parse_invalid_netloc(url):
	with pytest.raises(InvalidURI):
		URI(url)


@pytest.mark.parametrize('u', [b'Python', b'./Python', b'x-newscheme://foo.com/stuff', b'x://y', b'x:/y', b'x:/', b'/', ])
def test_unparse_parse(u):
	assert bytes(URI(u)) == u


@pytest.mark.parametrize('url,hostname,port', [
	(b'http://Test.python.org:5432/foo/', u'test.python.org', 5432),
	(b'http://12.34.56.78:5432/foo/', u'12.34.56.78', 5432),
	(b'http://[::1]:5432/foo/', u'::1', 5432),
	(b'http://[dead:beef::1]:5432/foo/', u'dead:beef::1', 5432),
	(b'http://[dead:beef::]:5432/foo/', u'dead:beef::', 5432),
	(b'http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]:5432/foo/', u'dead:beef:cafe:5417:affe:8fa3:deaf:feed', 5432),
	(b'http://[::12.34.56.78]:5432/foo/', u'::12.34.56.78', 5432),
	(b'http://[::ffff:12.34.56.78]:5432/foo/', u'::ffff:12.34.56.78', 5432),
	(b'http://Test.python.org/foo/', u'test.python.org', 80),
	(b'http://12.34.56.78/foo/', u'12.34.56.78', 80),
	(b'http://[::1]/foo/', u'::1', 80),
	(b'http://[dead:beef::1]/foo/', u'dead:beef::1', 80),
	(b'http://[dead:beef::]/foo/', u'dead:beef::', 80),
	(b'http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]/foo/', u'dead:beef:cafe:5417:affe:8fa3:deaf:feed', 80),
	(b'http://[::12.34.56.78]/foo/', u'::12.34.56.78', 80),
	(b'http://[::ffff:12.34.56.78]/foo/', u'::ffff:12.34.56.78', 80),
	(b'http://Test.python.org:/foo/', u'test.python.org', 80),
	(b'http://12.34.56.78:/foo/', u'12.34.56.78', 80),
	(b'http://[::1]:/foo/', u'::1', 80),
	(b'http://[dead:beef::1]:/foo/', u'dead:beef::1', 80),
	(b'http://[dead:beef::]:/foo/', u'dead:beef::', 80),
	(b'http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]:/foo/', u'dead:beef:cafe:5417:affe:8fa3:deaf:feed', 80),
	(b'http://[::12.34.56.78]:/foo/', u'::12.34.56.78', 80),
	(b'http://[::ffff:12.34.56.78]:/foo/', u'::ffff:12.34.56.78', 80),
])
def test_rfc2732(url, hostname, port):
	url = URI(url)
	assert url.hostname == hostname
	assert url.port == port


@pytest.mark.parametrize('url,hostname,port', [
	(b'http://[v123.:]/', u':', 80),
	(b'http://[v123.dead:beef]/', u'dead:beef', 80),
	(b'http://[v0.dead:beef]/', u'dead:beef', 80),
	(b'http://[v0.foo:123]/', u'foo:123', 80),
	(b'http://[v123.:]:1/', u':', 1),
	(b'http://[v123.dead:beef]:2/', u'dead:beef', 2),
	(b'http://[v0.dead:beef]:3/', u'dead:beef', 3),
	(b'http://[v0.foo:123]:4/', u'foo:123', 4),
	(b'http://[v0.fo[]o:123]:4/', u'fo[]o:123', 4),
])
def test_ipvfuture(url, hostname, port):
	url = URI(url)
	assert url.hostname == hostname
