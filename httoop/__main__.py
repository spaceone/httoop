# -*- coding: utf-8 -*-
"""httoop CLI tool.

Examples
--------
python3 -m httoop compose request -H 'Host: www.example.net'  | python3 -m httoop parse request
python3 -m httoop compose response  | python3 -m httoop parse response
"""

from __future__ import print_function

import sys
from argparse import ArgumentParser, FileType

from httoop import Request, Response, __name__ as name, __version__ as version
from httoop.client import ClientStateMachine
from httoop.server import ServerStateMachine


class CLI(object):
	"""httoop CLI tool."""

	def __init__(self):
		self.message = None
		self.parser = ArgumentParser(name, description=self.__doc__, epilog='https://github.com/spaceone/httoop/')
		self.parent_parser = ArgumentParser(add_help=False)
		self.parser.add_argument('-v', '--version', action='version', version='%%(prog)s %s' % (version,))
		self.add_subparsers()
		self.parse_arguments()

	def add_subparsers(self):
		action_subparsers = self.parser.add_subparsers(title="action", dest="action", required=True)
		parse_parser = action_subparsers.add_parser("parse", parents=[self.parent_parser])
		compose_parser = action_subparsers.add_parser("compose", parents=[self.parent_parser])

		compose_message_subparsers = compose_parser.add_subparsers(title="message", dest="message")
		request = compose_message_subparsers.add_parser("request", parents=[self.parent_parser])
		request.set_defaults(func=self.compose_request)
		add = request.add_argument
		add('-m', '--method')
		add('-u', '--uri')
		self.add_common_arguments(add)

		response = compose_message_subparsers.add_parser("response", parents=[self.parent_parser])
		response.set_defaults(func=self.compose_response)
		add = response.add_argument
		add('-s', '--status')
		add('--reason')
		self.add_common_arguments(add)

		parse_message_subparsers = parse_parser.add_subparsers(title="message", dest="message")
		request = parse_message_subparsers.add_parser("request", parents=[self.parent_parser])
		request.set_defaults(func=self.parse_request)
		add = request.add_argument
		add('--file', default='-', type=FileType('rb'))
		add('--scheme', default='http')
		add('--host', default='www.example.net')
		add('--port', default=80, type=int)

		response = parse_message_subparsers.add_parser("response", parents=[self.parent_parser])
		add = response.add_argument
		response.set_defaults(func=self.parse_response)
		add('--file', default='-', type=FileType('rb'))

	def parse_arguments(self):
		self.arguments = self.parser.parse_args()

		if self.arguments.action == 'parse' and hasattr(self.arguments.file, 'buffer'):
			# https://bugs.python.org/issue14156
			self.arguments.file = self.arguments.file.buffer
		self.arguments.func()

	def add_common_arguments(self, add) -> None:
		add('--protocol')
		add('-H', '--header', action='append', default=[])
		add('-b', '--body', default='')

	def parse_request(self):
		server = ServerStateMachine(self.arguments.scheme, self.arguments.host, self.arguments.port)
		for request, response in server.parse(self.arguments.file.read()):
			print(repr(response))
			print(repr(response.headers))
			print(repr(response.body))

	def parse_response(self):
		client = ClientStateMachine()
		client.request = Request()
		for response in client.parse(self.arguments.file.read()):
			print(repr(response))
			print(repr(response.headers))
			print(repr(response.body))
			print(repr(bytes(response.body)))
		if client.buffer:
			print('WARNING: response not yet complete!:')
			print(repr(client.message))
			print(repr(client.message.headers))
			print(repr(client.message.body))
			print(repr(client.buffer))

	def compose_request(self):
		self.message = Request()
		if self.arguments.method:
			self.message.method = self.arguments.method
		if self.arguments.uri:
			self.message.uri = self.arguments.uri
		self.common()

	def compose_response(self):
		self.message = Response()
		status = self.message.status.code
		if self.arguments.status:
			status = int(self.arguments.status)
		if self.arguments.reason:
			status = (status, self.arguments.reason)
		self.message.status = status
		self.common()

	def common(self):
		if self.arguments.protocol:
			protocol = self.arguments.protocol
			try:
				protocol = [int(x) for x in protocol.split('.', 1)]
			except ValueError:
				pass
			else:
				self.message.protocol = protocol
		for header in self.arguments.header:
			try:
				key, value = header.split(':', 1)
			except ValueError:
				continue
			self.message.headers[key.strip()] = value.strip()
		body = self.arguments.body
		if body == '-':
			body = sys.stdin.read()
		elif body.startswith('@'):
			body = open(body[1:], 'rb')
		self.message.body = body

		sys.stdout.write(self.decode(bytes(self.message)))
		sys.stdout.write(self.decode(bytes(self.message.headers)))
		sys.stdout.write(self.decode(bytes(self.message.body)))

	def decode(self, data):
		if str is not bytes:
			data = data.decode('ISO8859-1')
		return data


if __name__ == '__main__':
	CLI()
