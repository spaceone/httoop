# -*- coding: utf-8 -*-
import pytest
import datetime
import sys
from httoop import Headers
from httoop.exceptions import InvalidHeader


@pytest.fixture
def content_disposition():
	def _parse(header):
		h = Headers()
		h.parse(header)
		return h.elements('Content-Disposition')[0]
	return _parse


def test_inlonly(content_disposition):
	h = content_disposition('Content-Disposition: inline')
	assert h.inline
	assert h.filename is None
	assert not h.attachment


def test_inlonlyquoted(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: "inline"')


def test_inlwithasciifilename(content_disposition):
	h = content_disposition('Content-Disposition: inline; filename="foo.html"')
	assert h.inline
	assert not h.attachment
	assert h.filename == u'foo.html'


def test_inlwithfnattach(content_disposition):
	h = content_disposition('Content-Disposition: inline; filename="Not an attachment!"')
	assert h.inline
	assert not h.attachment
	assert h.filename == u'Not an attachment!'


def test_inlwithasciifilenamepdf(content_disposition):
	h = content_disposition('Content-Disposition: inline; filename="foo.pdf"')
	assert h.inline
	assert not h.attachment
	assert h.filename == 'foo.pdf'


def test_attonly(content_disposition):
	h = content_disposition('Content-Disposition: attachment')
	assert h.attachment
	assert not h.inline
	assert h.filename is None


def test_attonlyquoted(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: "attachment"')


@pytest.mark.xfail(reason=AssertionError('Cannot test here'))
def test_attonly403(content_disposition):
	h = content_disposition('Content-Disposition: attachment')
	assert False, 'Cannot test here'


def test_attonlyucase(content_disposition):
	h = content_disposition('Content-Disposition: ATTACHMENT')
	assert h.attachment
	assert not h.inline
	assert h.filename is None


def test_attwithasciifilename(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="foo.html"')
	assert h.attachment
	assert not h.inline
	assert h.filename == u'foo.html'


def test_attwithasciifilename25(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="0000000000111111111122222"')
	assert h.attachment
	assert not h.inline
	assert h.filename == u'0000000000111111111122222'


def test_attwithasciifilename35(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="00000000001111111111222222222233333"')
	assert h.attachment
	assert not h.inline
	assert h.filename == u'00000000001111111111222222222233333'


def test_attwithquotedsemicolon(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="Here\'s a semicolon;.html"')
	assert h.attachment
	assert h.filename == u"Here's a semicolon;.html"


def test_attwithasciifnescapedchar(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="f\\oo.html"')
	assert h.attachment
	assert not h.inline
	assert h.filename == u'foo.html'


def test_attwithasciifnescapedquote(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="\\"quoting\\" tested.html"')
	assert h.attachment
	assert h.filename == u'"quoting" tested.html'

def test_attwithfilenameandextparam(content_disposition):
	h = content_disposition('Content-Disposition: attachment; foo="bar"; filename="foo.html"')
	assert h.attachment
	assert h.params['foo'] == u'bar'
	assert h.filename == u'foo.html'


@pytest.mark.xfail(raises=InvalidHeader, reason='HeaderElement.RE_PARAMS.split')
def test_attwithfilenameandextparamescaped(content_disposition):
	h = content_disposition('Content-Disposition: attachment; foo="\\"\\\\";filename="foo.html"')
	assert h.attachment
	assert h.filename == u'foo.html'
	assert h.params['foo'] == u'"\\'


def test_attwithasciifilenameucase(content_disposition):
	h = content_disposition('Content-Disposition: attachment; FILENAME="foo.html"')
	assert h.attachment
	assert h.filename == u'foo.html'

def test_attwithasciifilenamenq(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename=foo.html')
	assert h.attachment
	assert h.filename == u'foo.html'

def test_attwithtokfncommanq(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename=foo,bar.html')

@pytest.mark.xfail(reason='Do we want to be that fussy?')
def test_attwithasciifilenamenqs(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename=foo.html ;')
	assert h.attachment
	assert h.filename == u'foo.html'


@pytest.mark.xfail(reason='Do we want to be that fussy?')
def test_attemptyparam(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; ;filename=foo')


def test_attwithasciifilenamenqws(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename=foo bar.html')


def test_attwithfntokensq(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename='foo.bar'")
	assert h.attachment
	assert h.filename == u"'foo.bar'"


def test_attwithisofnplain(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="foo-\xe4.html"')
	assert h.attachment
	assert h.filename == u'foo-\xe4.html'


def test_attwithutf8fnplain(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="foo-\xc3\xa4.html"')
	assert h.attachment
	assert h.filename == u'foo-\xc3\xa4.html'


def test_attwithfnrawpctenca(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="foo-%41.html"')
	assert h.attachment
	assert h.filename == u'foo-%41.html'

def test_attwithfnusingpct(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="50%.html"')
	assert h.attachment
	assert h.filename == u'50%.html'


def test_attwithfnrawpctencaq(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="foo-%\\41.html"')
	assert h.attachment
	assert h.filename == u'foo-%41.html'


def test_attwithnamepct(content_disposition):
	h = content_disposition('Content-Disposition: attachment; name="foo-%41.html"')
	assert h.attachment
	assert not h.filename
	assert h.params['name'] == u'foo-%41.html'


def test_attwithfilenamepctandiso(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="\xe4-%41.html"')
	assert h.attachment
	assert h.filename == u'\xe4-%41.html'


def test_attwithfnrawpctenclong(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="foo-%c3%a4-%e2%82%ac.html"')
	assert h.attachment
	assert h.filename == u'foo-%c3%a4-%e2%82%ac.html'


def test_attwithasciifilenamews1(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename ="foo.html"')
	assert h.attachment
	assert h.filename == u'foo.html'


def test_attwith2filenames(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename="foo.html"; filename="bar.html"')


def test_attfnbrokentoken(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename=foo[1](2).html')


@pytest.mark.xfail(reason='non-ascii currently allowed in header field params')
def test_attfnbrokentokeniso(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename=foo-\xe4.html')


@pytest.mark.xfail(reason='non-ascii currently allowed in header field params')
def test_attfnbrokentokenutf(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename=foo-\xc3\xa4.html')


def test_attmissingdisposition(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: filename=foo.html')

def test_attmissingdisposition2(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: x=y; filename=foo.html')


def test_attmissingdisposition3(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: "foo; filename=bar;baz"; filename=qux')


def test_attmissingdisposition4(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: filename=foo.html, filename=bar.html')


def test_emptydisposition(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: ; filename=foo.html')


def test_doublecolon(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: : inline; attachment; filename=foo.html')


def test_attandinline(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: inline; attachment; filename=foo.html')


def test_attandinline2(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; inline; filename=foo.html')


def test_attbrokenquotedfn(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename="foo.html".txt')


def test_attbrokenquotedfn2(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename="bar')


def test_attbrokenquotedfn3(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename=foo"bar;baz"qux')


@pytest.mark.xfail(reason='Content-Disposition is not marked as single-element-header')
def test_attmultinstances(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename=foo.html, attachment; filename=bar.html')


def test_attmissingdelim2(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename=bar foo=foo ')


def test_attmissingdelim3(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment filename=bar')


def test_attmissingdelim(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; foo=foo filename=bar')


def test_attreversed(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: filename=foo.html; attachment')


def test_attconfusedparam(content_disposition):
	h = content_disposition('Content-Disposition: attachment; xfilename=foo.html')
	assert h.attachment
	assert not h.filename
	assert h.params['xfilename'] == u'foo.html'


@pytest.mark.xfail(reason=AssertionError('Cannot test here'))
def test_attabspath(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="/foo.html"')
	assert h.attachment
	assert h.filename == u'/foo.html'
	assert False, 'Cannot test here'


def test_attabspathwin(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="\\\\foo.html"')
	assert h.attachment
	assert h.filename == u'\\foo.html'


def test_attcdate(content_disposition):
	h = content_disposition('Content-Disposition: attachment; creation-date="Wed, 12 Feb 1997 16:29:51 -0500"')

	assert h.creation_date == datetime.datetime(1997, 2, 12, 16, 29, 51)
	assert h.creation_date == 855761391.0


def test_attmdate(content_disposition):
	h = content_disposition('Content-Disposition: attachment; modification-date="Wed, 12 Feb 1997 16:29:51 -0500"')
	assert h.modification_date == datetime.datetime(1997, 2, 12, 16, 29, 51)
	assert h.modification_date == 855761391.0


@pytest.mark.xfail(reason='Currently only attachment|inline allowed. Subclass to allow further ones.')
def test_dispext(content_disposition):
	h = content_disposition('Content-Disposition: foobar')
	assert h.attachment
	assert not h.params


def test_dispextbadfn(content_disposition):
	h = content_disposition('Content-Disposition: attachment; example="filename=example.txt"')
	assert h.attachment
	assert not h.filename
	assert h.params['example'] == u'filename=example.txt'


def test_attwithisofn2231iso(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename*=iso-8859-1''foo-%E4.html")
	assert h.attachment
	assert h.filename == u'foo-\xe4.html'


def test_attwithfn2231utf8(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename*=UTF-8''foo-%c3%a4-%e2%82%ac.html")
	assert h.attachment
	assert h.filename == u'foo-\xe4-\u20ac.html'


def test_attwithfn2231noc(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename*=''foo-%c3%a4-%e2%82%ac.html")
	assert h.attachment
	assert not h.filename
	assert h.params['filename*'] == "''foo-%c3%a4-%e2%82%ac.html"


@pytest.mark.skipif(sys.platform != 'win32', reason='Windows specific')
@pytest.mark.xfail(sys.platform == 'win32', reason="Don't have a windows system to test")
def test_attwithfn2231utf8comp(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename*=UTF-8''foo-a%cc%88.html")
	assert h.attachment
	assert h.filename == u'foo-\xe4.html'


@pytest.mark.xfail(reason='Do we want to be that fussy?')
def test_attwithfn2231utf8_bad(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition("Content-Disposition: attachment; filename*=iso-8859-1''foo-%c3%a4-%e2%82%ac.html")


def test_attwithfn2231iso_bad(content_disposition):
	with pytest.raises(UnicodeDecodeError):
		h = content_disposition("Content-Disposition: attachment; filename*=utf-8''foo-%E4.html")


@pytest.mark.xfail(reason='Whitespace ignored in parameter (foo =bar)')
def test_attwithfn2231ws1(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition("Content-Disposition: attachment; filename *=UTF-8''foo-%c3%a4.html")


def test_attwithfn2231ws2(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename*= UTF-8''foo-%c3%a4.html")
	assert h.attachment
	assert h.filename == u'foo-\xe4.html'


def test_attwithfn2231ws3(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename* =UTF-8''foo-%c3%a4.html")
	assert h.attachment
	assert h.filename == u'foo-\xe4.html'


def test_attwithfn2231quot(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename*="UTF-8\'\'foo-%c3%a4.html"')
	assert h.params['filename*'] == u"UTF-8''foo-%c3%a4.html"


def test_attwithfn2231quot2(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename*="foo%20bar.html"')
	assert h.params['filename*'] == u'foo%20bar.html'


def test_attwithfn2231singleqmissing(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename*=UTF-8'foo-%c3%a4.html")
	assert h.params['filename*'] == u"UTF-8'foo-%c3%a4.html"


@pytest.mark.xfail(raises=KeyError, reason='Percent encoding does not raise errors')
def test_attwithfn2231nbadpct1(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename*=UTF-8''foo%")
	assert h.params['filename*'] == u"UTF-8''foo%"


@pytest.mark.xfail(raises=KeyError, reason='Percent encoding does not raise errors')
def test_attwithfn2231nbadpct2(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename*=UTF-8''f%oo.html")
	assert h.params['filename*'] == u"UTF-8''f%oo.html"


def test_attwithfn2231dpct(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename*=UTF-8''A-%2541.html")
	assert h.attachment
	assert h.filename == u'A-%41.html'


def test_attwithfn2231abspathdisguised(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename*=UTF-8''%5cfoo.html")
	assert h.attachment
	assert h.filename == u'\\foo.html'


def test_attfncont(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename*0="foo."; filename*1="html"')
	assert h.attachment
	assert h.filename == u'foo.html'


def test_attfncontqs(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename*0="foo"; filename*1="\\b\\a\\r.html"')
	assert h.filename == u'foobar.html'


def test_attfncontenc(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename*0*=UTF-8\'\'foo-%c3%a4; filename*1=".html"')
	assert h.attachment
	assert h.filename == u'foo-\xe4.html'


def test_attfncontlz(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename*0="foo"; filename*01="bar"')
	assert h.attachment
	assert h.filename == u'foo'
	assert h.params['filename*01'] == u'bar'


def test_attfncontnc(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename*0="foo"; filename*2="bar"')
	assert h.filename == u'foo'
	assert h.params['filename*2'] == u'bar'


def test_attfnconts1(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename*1="foo."; filename*2="html"')
	assert h.attachment
	assert h.filename is None
	assert h.params['filename*1'] == u'foo.'
	assert h.params['filename*2'] == u'html'


def test_attfncontord(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename*1="bar"; filename*0="foo"')
	assert h.attachment
	assert h.filename == u'foobar'


def test_attfnboth(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="foo-ae.html"; filename*=UTF-8\'\'foo-%c3%a4.html')
	assert h.attachment
	assert h.filename == u'foo-\xe4.html'


@pytest.mark.xfail(reason='Should be implemented generic')
def test_attfnboth2(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename*=UTF-8\'\'foo-%c3%a4.html; filename="foo-ae.html"')
	assert h.attachment
	assert h.filename == u'foo-\xe4.html'


@pytest.mark.xfail(reason='Should be implemented generic')
def test_attfnboth3(content_disposition):
	h = content_disposition("Content-Disposition: attachment; filename*0*=ISO-8859-15''euro-sign%3d%a4; filename*=ISO-8859-1''currency-sign%3d%a4")
	assert h.filename == u'currency-sign=\xa4'
	assert h.params['filename*0*'] == u"ISO-8859-15''euro-sign%3d%a4"


def test_attnewandfn(content_disposition):
	h = content_disposition('Content-Disposition: attachment; foobar=x; filename="foo.html"')
	assert h.attachment
	assert h.filename == u'foo.html'
	assert h.params['foobar'] == u'x'


@pytest.mark.xfail(reason='Generic parsing in Headers.parse(). Very complicated to implement.')
def test_attrfc2047token(content_disposition):
	with pytest.raises(InvalidHeader):
		h = content_disposition('Content-Disposition: attachment; filename==?ISO-8859-1?Q?foo-=E4.html?=')


def test_attrfc2047quoted(content_disposition):
	h = content_disposition('Content-Disposition: attachment; filename="=?ISO-8859-1?Q?foo-=E4.html?="')
	assert h.attachment
	assert h.filename == u'=?ISO-8859-1?Q?foo-=E4.html?='
