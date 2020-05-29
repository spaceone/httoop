from __future__ import unicode_literals
import pytest
from httoop import URI

RFC1808_BASE = b'http://a/b/c/d;p?q#f'
RFC2396_BASE = b'http://a/b/c/d;p?q'
RFC3986_BASE = b'http://a/b/c/d;p?q'
SIMPLE_BASE = b'http://a/b/c/d'

uri_join = {
	RFC3986_BASE: [
		# RFC 3986 Normal examples
		(b'g:h', b'g:h'),
		(b'g', b'http://a/b/c/g'),
		(b'./g', b'http://a/b/c/g'),
		(b'g/', b'http://a/b/c/g/'),
		(b'/g', b'http://a/g'),
		(b'//g', b'http://g'),
		(b'?y', b'http://a/b/c/d;p?y'),
		(b'g?y', b'http://a/b/c/g?y'),
		(b'#s', b'http://a/b/c/d;p?q#s'),
		(b'g#s', b'http://a/b/c/g#s'),
		(b'g?y#s', b'http://a/b/c/g?y#s'),
		(b';x', b'http://a/b/c/;x'),
		(b'g;x', b'http://a/b/c/g;x'),
		(b'g;x?y#s', b'http://a/b/c/g;x?y#s'),
		(b'', b'http://a/b/c/d;p?q'),
		(b'.', b'http://a/b/c/'),
		(b'./', b'http://a/b/c/'),
		(b'..', b'http://a/b/'),
		(b'../', b'http://a/b/'),
		(b'../g', b'http://a/b/g'),
		(b'../..', b'http://a/'),
		(b'../../', b'http://a/'),
		(b'../../g', b'http://a/g'),
		# RFC 3986 abnormal examples),
		(b'../../../g', b'http://a/g'),
		(b'../../../../g', b'http://a/g'),
		(b'/./g', b'http://a/g'),
		(b'/../g', b'http://a/g'),
		(b'g.', b'http://a/b/c/g.'),
		(b'.g', b'http://a/b/c/.g'),
		(b'g..', b'http://a/b/c/g..'),
		(b'..g', b'http://a/b/c/..g'),
		(b'./../g', b'http://a/b/g'),
		(b'./g/.', b'http://a/b/c/g/'),
		(b'g/./h', b'http://a/b/c/g/h'),
		(b'g/../h', b'http://a/b/c/h'),
		(b'g;x=1/./y', b'http://a/b/c/g;x=1/y'),
		(b'g;x=1/../y', b'http://a/b/c/y'),
		(b'g?y/./x', b'http://a/b/c/g?y/./x'),
		(b'g?y/../x', b'http://a/b/c/g?y/../x'),
		(b'g#s/./x', b'http://a/b/c/g#s/./x'),
		(b'g#s/../x', b'http://a/b/c/g#s/../x'),
		(b'http:g', b'http:g'),
		# own examples
		(b'//', b'http://a/b/c/d;p?q'),
		(b'g%3ah', b'http://a/b/c/g:h'),
	],
	SIMPLE_BASE: [
		(b'g:h', b'g:h'),
		#(b'http:g', b'http://a/b/c/g'),
		#(b'http:', b'http://a/b/c/d'),
		(b'g', b'http://a/b/c/g'),
		(b'./g', b'http://a/b/c/g'),
		(b'g/', b'http://a/b/c/g/'),
		(b'/g', b'http://a/g'),
		(b'//g', b'http://g'),
		(b'?y', b'http://a/b/c/d?y'),
		(b'g?y', b'http://a/b/c/g?y'),
		(b'g?y/./x', b'http://a/b/c/g?y/./x'),
		(b'.', b'http://a/b/c/'),
		(b'./', b'http://a/b/c/'),
		(b'..', b'http://a/b/'),
		(b'../', b'http://a/b/'),
		(b'../g', b'http://a/b/g'),
		(b'../..', b'http://a/'),
		(b'../../g', b'http://a/g'),
		(b'./../g', b'http://a/b/g'),
		(b'./g/.', b'http://a/b/c/g/'),
		(b'g/./h', b'http://a/b/c/g/h'),
		(b'g/../h', b'http://a/b/c/h'),
		#(b'http:g', b'http://a/b/c/g'),
		#(b'http:', b'http://a/b/c/d'),
		#(b'http:?y', b'http://a/b/c/d?y'),
		#(b'http:g?y', b'http://a/b/c/g?y'),
		#(b'http:g?y/./x', b'http://a/b/c/g?y/./x'),
	],
	RFC2396_BASE: [
		(b'g:h', b'g:h'),
		(b'g', b'http://a/b/c/g'),
		(b'./g', b'http://a/b/c/g'),
		(b'g/', b'http://a/b/c/g/'),
		(b'/g', b'http://a/g'),
		(b'//g', b'http://g'),
		(b'g?y', b'http://a/b/c/g?y'),
		(b'#s', b'http://a/b/c/d;p?q#s'),
		(b'g#s', b'http://a/b/c/g#s'),
		(b'g?y#s', b'http://a/b/c/g?y#s'),
		(b'g;x', b'http://a/b/c/g;x'),
		(b'g;x?y#s', b'http://a/b/c/g;x?y#s'),
		(b'.', b'http://a/b/c/'),
		(b'./', b'http://a/b/c/'),
		(b'..', b'http://a/b/'),
		(b'../', b'http://a/b/'),
		(b'../g', b'http://a/b/g'),
		(b'../..', b'http://a/'),
		(b'../../', b'http://a/'),
		(b'../../g', b'http://a/g'),
		(b'', RFC2396_BASE),
		(b'g.', b'http://a/b/c/g.'),
		(b'.g', b'http://a/b/c/.g'),
		(b'g..', b'http://a/b/c/g..'),
		(b'..g', b'http://a/b/c/..g'),
		(b'./../g', b'http://a/b/g'),
		(b'./g/.', b'http://a/b/c/g/'),
		(b'g/./h', b'http://a/b/c/g/h'),
		(b'g/../h', b'http://a/b/c/h'),
		(b'g;x=1/./y', b'http://a/b/c/g;x=1/y'),
		(b'g;x=1/../y', b'http://a/b/c/y'),
		(b'g?y/./x', b'http://a/b/c/g?y/./x'),
		(b'g?y/../x', b'http://a/b/c/g?y/../x'),
		(b'g#s/./x', b'http://a/b/c/g#s/./x'),
		(b'g#s/../x', b'http://a/b/c/g#s/../x'),
	],
	# "normal" cases from RFC 1808:
	RFC1808_BASE: [
		(b'g:h', b'g:h'),
		(b'g', b'http://a/b/c/g'),
		(b'./g', b'http://a/b/c/g'),
		(b'g/', b'http://a/b/c/g/'),
		(b'/g', b'http://a/g'),
		(b'//g', b'http://g'),
		(b'g?y', b'http://a/b/c/g?y'),
		(b'g?y/./x', b'http://a/b/c/g?y/./x'),
		(b'#s', b'http://a/b/c/d;p?q#s'),
		(b'g#s', b'http://a/b/c/g#s'),
		(b'g#s/./x', b'http://a/b/c/g#s/./x'),
		(b'g?y#s', b'http://a/b/c/g?y#s'),
		(b'g;x', b'http://a/b/c/g;x'),
		(b'g;x?y#s', b'http://a/b/c/g;x?y#s'),
		(b'.', b'http://a/b/c/'),
		(b'./', b'http://a/b/c/'),
		(b'..', b'http://a/b/'),
		(b'../', b'http://a/b/'),
		(b'../g', b'http://a/b/g'),
		(b'../..', b'http://a/'),
		(b'../../', b'http://a/'),
		(b'../../g', b'http://a/g'),

		(b'', b'http://a/b/c/d;p?q#f'),
		(b'g.', b'http://a/b/c/g.'),
		(b'.g', b'http://a/b/c/.g'),
		(b'g..', b'http://a/b/c/g..'),
		(b'..g', b'http://a/b/c/..g'),
		(b'./../g', b'http://a/b/g'),
		(b'./g/.', b'http://a/b/c/g/'),
		(b'g/./h', b'http://a/b/c/g/h'),
		(b'g/../h', b'http://a/b/c/h'),
	]
}

further = [
	(b'http://a/b/c/de', b';x', b'http://a/b/c/;x'),
	(b'a', b'b', b'b'),  # don't duplicate filename
	#pytest.mark.xfail((b'http:///', b'..','http:///'), reason='The // is stripped due to normalization.'),
	(b'', b'http://a/b/c/g?y/./x', b'http://a/b/c/g?y/./x'),
	#pytest.mark.xfail((b'', b'http://a/./g', b'http://a/./g'), reason='The dot is stripped due to normalization'),
	(b'svn://pathtorepo/dir1', b'dir2', b'svn://pathtorepo/dir2'),
	(b'svn+ssh://pathtorepo/dir1', b'dir2', b'svn+ssh://pathtorepo/dir2'),
	(SIMPLE_BASE + b'/', b'foo', SIMPLE_BASE + b'/foo'),
	(b'http://a/b/c/d/e/', b'../../f/g/', b'http://a/b/c/f/g/'),
	(b'http://a/b/c/d/e', b'../../f/g/', b'http://a/b/f/g/'),
	(b'http://a/b/c/d/e/', b'/../../f/g/', b'http://a/f/g/'),
	(b'http://a/b/c/d/e', b'/../../f/g/', b'http://a/f/g/'),
	(b'http://a/b/c/d/e/', b'../../f/g', b'http://a/b/c/f/g'),
	(b'http://a/b/', b'../../f/g/', b'http://a/f/g/'),
]
for base, rel, abs_ in further:
	uri_join.setdefault(base, []).append((rel, abs_))


@pytest.mark.parametrize('base,relative,expected', [(base, relative, expected) for base, relative_expected in uri_join.items() for (relative, expected) in relative_expected])
def test_uri_join(base, relative, expected):
	uri = URI(base).join(relative)
	assert uri == expected


@pytest.mark.parametrize('base,relative,expected', [(base, relative, expected) for base, relative_expected in uri_join.items() for (relative, expected) in relative_expected])
def test_uri_join_very_strict(base, relative, expected):
	uri = URI(base).join(relative)
	assert bytes(uri) == bytes(expected)
#@pytest.mark.parametrize('expected,got,relative', [(expected, bytes(URI(base).join(relative)), relative) for base, relative_expected in uri_join.items() for (relative, expected) in relative_expected])
#def test_uri_join_very_strict(expected, got, relative):
#	assert expected == got
