from httoop import InvalidHeader

def test_multiple_same_headers():
	pass

def test_header_case_insensitivity():
	pass

def test_header_with_continuation_lines(headers):
	headers.parse('Foo: bar\r\n baz')
	headers.parse('Foo2: bar\r\n\tbaz')
	headers.parse('Foo3: bar\r\n  baz')
	headers.parse('Foo4: bar\r\n\t baz')
	assert headers['Foo'] == 'barbaz'
	assert headers['Foo2'] == 'barbaz'
	assert headers['Foo3'] == 'bar baz'
	assert headers['Foo4'] == 'bar baz'

def test_request_without_headers():
	pass

def test_invalid_header_syntax(headers):
	invalid_headers = ['Foo']
	for char in b"%s\x7F()<>@,;\\\\\"/\[\]?={} \t%s" % (b''.join(map(chr, range(0x00, 0x1F))), ''.join(map(chr, range(0x80, 0xFF)))):
		invalid_headers.append(b'Fo%so: bar' % (char,))
	for invalid in invalid_headers:
		try:
			headers.parse(invalid)
		except InvalidHeader:
			pass
		else:
			assert False, 'Invalid header %r parsed successfully' % (invalid,)
