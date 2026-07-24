from io import BytesIO, StringIO
from tempfile import NamedTemporaryFile

import pytest

from httoop import Body, Request


def test_body_set_unicode(request_: Request):
    request_.body = 'foobar'
    assert bytes(request_.body) == b'foobar'
    assert str(request_.body) == 'foobar'
    assert request_.body.fileable


def test_body_set_bytes(request_: Request):
    request_.body = b'foobar'
    assert bytes(request_.body) == b'foobar'
    assert str(request_.body) == 'foobar'
    assert request_.body.fileable


def test_body_set_bytesio(request_: Request):
    b = BytesIO(b'ThisIsABytesIOBody')
    request_.body = b
    assert bytes(request_.body) == b'ThisIsABytesIOBody'
    assert str(request_.body) == 'ThisIsABytesIOBody'
    assert request_.body.fileable


def test_body_set_stringio(request_: Request):
    s = StringIO('ThisIsAStringIOBody')
    request_.body = s
    assert bytes(request_.body) == b'ThisIsAStringIOBody'
    assert str(request_.body) == 'ThisIsAStringIOBody'
    assert request_.body.fileable


def test_body_set_tempfile(request_: Request):
    with NamedTemporaryFile() as tempfile:
        tempfile.write(b'ThisIsANamedTemporaryFile')
        tempfile.flush()
        request_.body = tempfile
        assert len(request_.body) == 25
        assert request_.body == b'ThisIsANamedTemporaryFile'
        assert request_.body.fileable


def test_body_set_bytearray(request_: Request):
    a = bytearray(b''.join([b'We', b'', b'are ', b'just', b' ', b'testing\t', b'ByteArrays!']))
    request_.body = a
    assert bytes(request_.body) == b'Weare just testing\tByteArrays!'


def test_body_set_list(request_: Request):
    ls = ['This ', 'is', b'\nsome', None, 'list\t', 'content', '']
    request_.body = ls
    assert bytes(request_.body) == b'This is\nsomelist\tcontent'


def test_body_set_tuple(request_: Request):
    t = ('Testing', ' ', 'a', 'tuple')
    request_.body = t
    assert bytes(request_.body) == b'Testing atuple'


def test_body_set_generator(request_: Request):
    def g():
        yield 'This '
        yield 'is'
        yield ' '
        yield
        yield 'A'
        yield '\t'
        yield 'Generator'

    request_.body = g()
    assert request_.body.generator
    assert bytes(request_.body) == b'This is A\tGenerator'
    assert str(request_.body) == 'This is A\tGenerator'
    assert bytes(request_.body) == b'This is A\tGenerator'
    assert len(request_.body) == 19


def test_body_set_body(request_: Request):
    b = Body()
    b.mimetype = 'application/json'
    b.set('{}')
    request_.body = b
    assert request_.body.mimetype == 'application/json'
    assert bytes(request_.body) == b'{}'
    assert request_.body.fd is b.fd


def test_body_iterencode(request_: Request):
    request_.body.mimetype = 'application/json'
    request_.body.iterencode({})
    assert bytes(request_.body) == b'{}'


def tets_body_set_none(request_: Request):
    request_.body = 'Foobar'
    request_.body = None
    assert not request_.body
    assert bytes(request_.body) == b''


def test_closed_body(request_: Request):
    b = BytesIO()
    b.close()
    with pytest.raises(ValueError, match=r'I/O operation on closed file\.'):
        request_.body = b


def test_body_close_clear(request_: Request):
    request_.body = b'asfd asdf asdf asdf asdf asdf asdf'
    assert request_.body
    request_.body.close()
    assert not request_.body
    assert len(request_.body) == 0
    assert bytes(request_.body) == b''


def test_empty_body_is_false(request_: Request):
    request_.body = 'foobar'
    assert request_.body
    assert len(request_.body) == 6
    request_.body = None
    assert not request_.body
    assert len(request_.body) == 0


def test_set_invalid_body(request_: Request):
    with pytest.raises(TypeError):
        request_.body = 1


def test_body_iter_list(request_: Request):
    request_.body = ['asdf', 'foo', 'Ba', 'Baz', None, 'blub']
    assert next(request_.body) == b'asdf'
    assert next(request_.body) == b'foo'
    assert next(request_.body) == b'Ba'
    assert next(request_.body) == b'Baz'
    assert next(request_.body) == b'blub'
    with pytest.raises(StopIteration):
        next(request_.body)
    assert next(request_.body) == b'asdf'
    assert next(request_.body) == b'foo'
    assert next(request_.body) == b'Ba'
    assert next(request_.body) == b'Baz'
    assert next(request_.body) == b'blub'


def test_body_file_interface(request_: Request):
    assert request_.body.name is None
    request_.body.flush()
    request_.body = b'foo\nbar\nbaz\nblub'
    assert request_.body.readline() == b'foo\n'
    assert request_.body.readlines(7) == [b'bar\n', b'baz\n']
    request_.body.seek(3)
    request_.body.truncate()
    assert bytes(request_.body) == b'foo'
    request_.body.writelines([b'bar\n', b'Baz'])
    assert bytes(request_.body) == b'foobar\nBaz'
