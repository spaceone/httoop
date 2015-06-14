

class ComposedMessage(object):

	# FIXME: use it
	@property
	def close(self):
		# TODO: find out why this constraint
		return 'Transfer-Encoding' in self.message.headers and 'chunked' not in self.message.headers.elements('Transfer-Encoding')

	@property
	def transfer_encoding(self):
		return self.message.headers.elements('Transfer-Encoding')

	@transfer_encoding.setter
	def transfer_encoding(self, transfer_encoding):
		if transfer_encoding:
			self.message.headers['Transfer-Encoding'] = bytes(transfer_encoding)
		#	self.message.transfer_codec = None  #self.message.transfer_encoding.iterdecode()
		else:
			self.message.headers.pop('Transfer-Encoding', None)
		#	self.message.transfer_codec = None

	@property
	def chunked(self):
		return 'chunked' in self.message.headers.elements("Transfer-Encoding")

	@chunked.setter
	def chunked(self, chunked):
		self.message.body.chunked = chunked
		if chunked:
			self.message.headers.pop('Content-Length', None)
			if self.chunked:
				return
			self.message.headers.append('Transfer-Encoding', 'chunked')
		else:
			if not self.chunked:
				return
			te = self.message.headers.elements('Transfer-Encoding')
			te.remove('chunked')
			self.message.headers['Transfer-Encoding'] = b''.join(map(bytes, te))

	def __iter__(self):
		start_line = bytes(self.message)
		headers = bytes(self.message.headers)
		yield start_line + headers
		for data in self.message.body:
			yield data
