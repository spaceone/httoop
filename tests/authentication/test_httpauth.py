# -*- coding: utf-8 -*-
"""Implement test cases from:
http://test.greenbytes.de/tech/tc/httpauth/
"""

import pytest
from httoop import Headers
from httoop.exceptions import InvalidHeader


@pytest.fixture
def authentication():
	def _parse(header):
		h = Headers()
		h.parse(header)
		return h.elements('WWW-Authenticate')[0]
	return _parse


def test_simplebasic(authentication):
	"""simple Basic auth"""
	a = authentication(b'WWW-Authenticate: Basic realm="foo"')


@pytest.mark.xfail(reason='FIXME')
@pytest.mark.skip(reason='TODO')
def test_simplebasiclf(authentication):
	"""simple Basic auth, with (deprecated) line folding"""
	a = authentication(b'WWW-Authenticate: Basic\r\n realm="foo"')


def test_simplebasicucase(authentication):
	"""simple Basic auth (using uppercase characters)"""
	a = authentication(b'WWW-Authenticate: BASIC REALM="foo"')


def test_simplebasictok(authentication):  # invalidsyntax
	"""simple Basic auth, using token format for realm (but see <a href="http://greenbytes.de/tech/webdav/draft-ietf-httpbis-p7-auth-25.html#rfc.section.2.2.p.4">Section 2.2 of draft-ietf-httpbis-p7-auth-22</a>)"""
	a = authentication(b'WWW-Authenticate: Basic realm=foo')


def test_simplebasictokbs(authentication):  # parseerror
	"""simple Basic auth, using token format for realm (but see <a href="http://greenbytes.de/tech/webdav/draft-ietf-httpbis-p7-auth-22.html#rfc.section.2.2.p.4">Section 2.2 of draft-ietf-httpbis-p7-auth-22</a>), including backslashes"""
	with pytest.raises(InvalidHeader):
		a = authentication(b'WWW-Authenticate: Basic realm=\\f\o\o')


def test_simplebasicsq(authentication):  # invalidsyntax
	"""simple Basic auth, using single quotes (these are allowed in a token, but should not be treated as quote characters)"""
	with pytest.raises(InvalidHeader):
		a = authentication(b"Basic realm='foo'")


def test_simplebasicpct(authentication):
	"""simple Basic auth, containing a %-escape (which isn't special here)"""
	a = authentication(b'WWW-Authenticate: Basic realm="foo%20bar"')


def test_simplebasiccomma(authentication):
	"""simple Basic auth, with a comma between schema and auth-param"""
	a = authentication(b'WWW-Authenticate: Basic , realm="foo"')


def test_simplebasiccomma2(authentication):  # parseerror
	"""simple Basic auth, with a comma between schema and auth-param (this is invalid because of the missing space characters after the scheme name)"""
	with pytest.raises(InvalidHeader):
		a = authentication(b'WWW-Authenticate: Basic, realm="foo"')


def test_simplebasicnorealm(authentication):  # parseerror
	"""simple Basic auth, realm parameter missing"""
	with pytest.raises(InvalidHeader):
		a = authentication(b'WWW-Authenticate: Basic')


def test_simplebasic2realms(authentication):  # invalidsyntax
	"""simple Basic auth with two realm parameters"""
	a = authentication(b'WWW-Authenticate: Basic realm="foo", realm="bar"')


def test_simplebasicwsrealm(authentication):
	"""simple Basic auth, (bad) whitespace used in auth-param assignment"""
	with pytest.raises(InvalidHeader):
		a = authentication(b'WWW-Authenticate: Basic realm = "foo"')


def test_simplebasicrealmsqc(authentication):
	"""simple Basic auth, with realm using quoted string escapes"""
	a = authentication(b'WWW-Authenticate: Basic realm="\f\o\o"')


def test_simplebasicrealmsqc2(authentication):
	"""simple Basic auth, with realm using quoted string escapes"""
	a = authentication(b'WWW-Authenticate: Basic realm="\"foo\""')


@pytest.mark.xfail(reason='TODO?')
def test_simplebasicnewparam1(authentication):
	"""simple Basic auth, with additional auth-params"""
	a = authentication(b'WWW-Authenticate: Basic realm="foo", bar="xyz",, a=b,,,c=d')


def test_simplebasicnewparam2(authentication):
	"""simple Basic auth, with an additional auth-param (but with reversed order)"""
	a = authentication(b'WWW-Authenticate: Basic bar="xyz", realm="foo"')


def test_simplebasicrealmiso88591(authentication):
	"""simple Basic auth, using "a umlaut" character encoded using ISO-8859-1"""
	a = authentication(b'WWW-Authenticate: Basic realm="foo-ä"')


def test_simplebasicrealmutf8(authentication):
	"""simple Basic auth, using "a umlaut" character encoded using UTF-8"""
	a = authentication(b'WWW-Authenticate: Basic realm="foo-\xc3\xa4"')


def test_simplebasicrealmrfc2047(authentication):
	"""simple Basic auth, using "a umlaut" character encoded using RFC 2047"""
	a = authentication(b'WWW-Authenticate: Basic realm="=?ISO-8859-1?Q?foo-=E4?="')
	# <tc:expectation>RFC 2047 does not apply to quoted-strings, so the realm really is <code>=?ISO-8859-1?Q?foo-=E4?=</code></tc:expectation>


@pytest.mark.xfail(reason='FIXME')
def test_multibasicunknown(authentication):
	"""a header field containing two challenges, one of which unknown"""
	a = authentication(b'WWW-Authenticate: Basic realm="basic", Newauth realm="newauth"')


@pytest.mark.xfail(reason='FIXME')
def test_multibasicunknown2(authentication):
	"""as above, but with challenges swapped"""
	a = authentication(b'WWW-Authenticate: Newauth realm="newauth", Basic realm="basic"')


@pytest.mark.xfail(reason='FIXME')
def test_multibasicunknown2mf(authentication):  # TODO
	a = authentication(b'WWW-Authenticate: Newauth realm="newauth"')
	a = authentication(b'WWW-Authenticate: Basic realm="basic"')
	"""as above, but using two header fields"""


@pytest.mark.xfail(reason='FIXME')
def test_multibasicempty(authentication):
	"""a header field containing one Basic challenge, following an empty one"""
	a = authentication(b'WWW-Authenticate: ,Basic realm="basic"')


@pytest.mark.xfail(reason='FIXME')
def test_multibasicqs(authentication):
	"""a header field containing two challenges, the first one for a new scheme and having a parameter using quoted-string syntax"""
	a = authentication(b'WWW-Authenticate: Newauth realm="apps", type=1, title="Login to \"apps\"", Basic realm="simple" ')


@pytest.mark.xfail(reason='FIXME')
def test_multidisgscheme(authentication):
	"""a header field containing two challenges, the first one for a new scheme and having a parameter called "Basic" """
	a = authentication(b'WWW-Authenticate: Newauth realm="Newauth Realm", basic=foo, Basic realm="Basic Realm" ')


@pytest.mark.xfail(reason='FIXME')
def test_unknown(authentication):
	"""a header field containing a challenge for an unknown scheme"""
	a = authentication(b'WWW-Authenticate: Newauth realm="newauth"')


def test_disguisedrealm(authentication):
	"""a header field containing a Basic challenge, with a quoted-string extension param that happens to contain the string "realm=" """
	a = authentication(b'WWW-Authenticate: Basic foo="realm=nottherealm", realm="basic"')


def test_disguisedrealm2(authentication):
	"""a header field containing a Basic challenge, with a preceding extension param named "nottherealm" """
	a = authentication(b'WWW-Authenticate: Basic nottherealm="nottherealm", realm="basic"')


@pytest.mark.xfail(reason='FIXME')
def test_missingquote(authentication):  # parseerror
	"""a header field containing a Basic challenge, with a realm missing the second double quote"""
	with pytest.raises(InvalidHeader):
		a = authentication(b'WWW-Authenticate: Basic realm="basic')
