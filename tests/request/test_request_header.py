from httoop import Headers, InvalidHeader

def test_multiple_same_headers():
	pass

def test_header_case_insensitivity():
	pass

def test_header_with_continuation_lines():
	h = Headers()
	h.parse('Foo: bar\r\n baz')
	h.parse('Foo2: bar\r\n\tbaz')
	h.parse('Foo3: bar\r\n  baz')
	h.parse('Foo4: bar\r\n\t baz')
	assert h['Foo'] == 'barbaz'
	assert h['Foo2'] == 'barbaz'
	assert h['Foo3'] == 'bar baz'
	assert h['Foo4'] == 'bar baz'

def test_request_without_headers():
	pass

def test_invalid_header_syntax():
	h = Headers()
	invalid_headers = ['Foo']
	for char in b"%s\x7F()<>@,;\\\\\"/\[\]?={} \t%s" % (b''.join(map(chr, range(0x00, 0x1F))), ''.join(map(chr, range(0x80, 0xFF)))):
		invalid_headers.append(b'Fo%so: bar' % (char,))
	for invalid in invalid_headers:
		try:
			h.parse(invalid)
		except InvalidHeader:
			pass
		else:
			assert False, 'Invalid header %r parsed successfully' % (invalid,)
