import pytest
from httoop import URI


@pytest.mark.parametrize('url,expected', (
	('ftp://ftp.is.co.za/rfc/rfc1808.txt', (u'ftp', u'', u'', u'ftp.is.co.za', 21, u'/rfc/rfc1808.txt', u'', u'')),
	('http://www.ietf.org/rfc/rfc2396.txt', (u'http', u'', u'', u'www.ietf.org', 80, u'/rfc/rfc2396.txt', u'', u'')),
	pytest.mark.skipif(True, ('ldap://[2001:db8::7]/c=GB?objectClass?one', (u'ldap', u'', u'', u'[2001:db8::7]', 389, u'/c=GB', u'objectClass?one', u'')), reason='Parse query in ldap URI?'),
	('mailto:John.Doe@example.com', (u'mailto', u'', u'', u'', None, u'John.Doe@example.com', u'', u'')),
	('news:comp.infosystems.www.servers.unix', (u'news', u'', u'', u'', None, u'comp.infosystems.www.servers.unix', u'', u'')),
	('tel:+1-816-555-1212', (u'tel', u'', u'', u'', None, u'+1-816-555-1212', u'', u'')),
	('telnet://192.0.2.16:80/', (u'telnet', u'', u'', u'192.0.2.16', 80, u'/', u'', u'')),
	('urn:oasis:names:specification:docbook:dtd:xml:4.1.2', (u'urn', u'', u'', u'', None, u'oasis:names:specification:docbook:dtd:xml:4.1.2', u'', u'')),
	('file:///tmp/junk.txt', (u'file', u'', u'', u'', None, u'/tmp/junk.txt', u'', u'')),
	('imap://mail.python.org/mbox1', (u'imap', u'', u'', u'mail.python.org', 143, u'/mbox1', u'', u'')),
	('mms://wms.sys.hinet.net/cts/Drama/09006251100.asf', (u'mms', u'', u'', u'wms.sys.hinet.net', 1755, u'/cts/Drama/09006251100.asf', u'', u'')),
	('nfs://server/path/to/file.txt', (u'nfs', u'', u'', u'server', 2049, u'/path/to/file.txt', u'', u'')),
	('svn+ssh://svn.zope.org/repos/main/ZConfig/trunk/', (u'svn+ssh', u'', u'', u'svn.zope.org', 22, u'/repos/main/ZConfig/trunk/', u'', u'')),
	('git+ssh://git@github.com/user/project.git', (u'git+ssh', u'git', u'', u'github.com', 22, u'/user/project.git', u'', u'')),
))
def test_parse_scheme(url, expected):
	uri = URI(url)
	assert uri.tuple == expected
	assert bytes(uri) == bytes(URI(expected))
