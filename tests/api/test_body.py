import pytest
from io import BytesIO, StringIO
from tempfile import NamedTemporaryFile

try:
	unicode
except NameError:
	unicode = str


def test_body_set_unicode(request):
	request.body = u'foobar'
	assert bytes(request.body) == b'foobar'
	assert unicode(request.body) == u'foobar'
	assert request.body.fileable


def test_body_set_bytes(request):
	request.body = b'foobar'
	assert bytes(request.body) == b'foobar'
	assert unicode(request.body) == u'foobar'
	assert request.body.fileable


def test_body_set_bytesio(request):
	b = BytesIO(b'ThisIsABytesIOBody')
	request.body = b
	assert bytes(request.body) == b'ThisIsABytesIOBody'
	assert unicode(request.body) == u'ThisIsABytesIOBody'
	assert request.body.fileable


def test_body_set_stringio(request):
	s = StringIO(u'ThisIsAStringIOBody')
	request.body = s
	assert bytes(request.body) == b'ThisIsAStringIOBody'
	assert unicode(request.body) == u'ThisIsAStringIOBody'
	assert request.body.fileable


def test_body_set_tempfile(request):
	tempfile = NamedTemporaryFile()
	tempfile.write(b'ThisIsANamedTemporaryFile')
	tempfile.flush()
	request.body = tempfile
	assert len(request.body) == 25
	assert request.body == b'ThisIsANamedTemporaryFile'
	assert request.body.fileable
	tempfile.close()


def test_body_set_bytearray(request):
	a = bytearray(''.join([b'We', b'', b'are ', b'just', b' ', b'testing\t', b'ByteArrays!']))
	request.body = a
	assert bytes(request.body) == b'Weare just testing\tByteArrays!'


def test_body_set_list(request):
	l = [u'This ', 'is', b'\nsome', None, u'list\t', 'content', '']
	request.body = l
	assert bytes(request.body) == b'This is\nsomelist\tcontent'


def test_body_set_tuple(request):
	t = ('Testing', ' ', 'a', 'tuple')
	request.body = t
	assert bytes(request.body) == b'Testing atuple'


def test_body_set_generator(request):
	def g():
		yield 'This '
		yield 'is'
		yield ' '
		yield
		yield 'A'
		yield '\t'
		yield 'Generator'
	request.body = g()
	assert request.body.generator
	assert bytes(request.body) == b'This is A\tGenerator'
	assert unicode(request.body) == u'This is A\tGenerator'
	assert bytes(request.body) == b'This is A\tGenerator'
	assert len(request.body) == 19


def test_body_set_body(request):
	pass


def tets_body_set_none(request):
	request.body = 'Foobar'
	request.body = None
	assert not request.body
	assert bytes(request.body) == b''


def test_closed_body(request):
	b = BytesIO()
	b.close()
	with pytest.raises(ValueError):
		request.body = b


def test_body_close_clear(request):
	request.body = b'asfd asdf asdf asdf asdf asdf asdf'
	assert request.body
	request.body.close()
	assert not request.body
	assert len(request.body) == 0
	assert bytes(request.body) == b''


def test_empty_body_is_false(request):
	request.body = 'foobar'
	assert request.body
	assert len(request.body) == 6
	request.body = None
	assert not request.body
	assert len(request.body) == 0


def test_set_invalid_body(request):
	with pytest.raises(TypeError):
		request.body = 1


def test_body_iter_list(request):
	request.body = ['asdf', 'foo', 'Ba', 'Baz', None, 'blub']
	assert next(request.body) == 'asdf'
	assert next(request.body) == 'foo'
	assert next(request.body) == 'Ba'
	assert next(request.body) == 'Baz'
	assert next(request.body) == 'blub'
	with pytest.raises(StopIteration):
		next(request.body)
	assert next(request.body) == 'asdf'
	assert next(request.body) == 'foo'
	assert next(request.body) == 'Ba'
	assert next(request.body) == 'Baz'
	assert next(request.body) == 'blub'
