# -*- coding: utf-8 -*-
"""httoop CLI tool."""

from __future__ import print_function

import sys
from argparse import ArgumentParser

from httoop import __version__ as version, __name__ as name
from httoop import Request, Response


class CLI(object):

	def __init__(self):
		self.message = None
		self.parser = ArgumentParser(name, version=str(version), description=__doc__, epilog='https://github.com/spaceone/httoop/')
	#	self.parser.add_argument('--parse')
	#	self.parser.add_argument('--validate', action='store_true')
		self.parsers = self.parser.add_subparsers(dest='type')
		self.modes = {
			'request': self.request,
			'response': self.response,
			'parse': {
				'request': self.parse_request,
				'response': self.parse_response,
			}
		}
		self.add_subparsers()
		self.parse_arguments()

	def add_subparsers(self):
		request = self.parsers.add_parser('request')
		add = request.add_argument
		add('-m', '--method')
		add('-u', '--uri')
		self.add_common_arguments(add)

		response = self.parsers.add_parser('response')
		add = response.add_argument
		add('-s', '--status')
		add('--reason')
		self.add_common_arguments(add)

	def parse_arguments(self):
		self.arguments = self.parser.parse_args()
		cb = self.modes[self.arguments.type]
		cb()

	def add_common_arguments(self, add):
		add('--protocol')
		add('-H', '--header', action='append', default=[])
		add('-b', '--body', default='')

	def parse_request(self):
		raise NotImplementedError('TODO')

	def parse_response(self):
		raise NotImplementedError('TODO')

	def request(self):
		self.message = Request()
		if self.arguments.method:
			self.message.method = self.arguments.method
		if self.arguments.uri:
			self.message.uri = self.arguments.uri
		self.common()

	def response(self):
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
				protocol = map(int, protocol.split('.', 1))
			except ValueError:
				pass
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

		sys.stdout.write(bytes(self.message))
		sys.stdout.write(bytes(self.message.headers))
		sys.stdout.write(bytes(self.message.body))


if __name__ == '__main__':
	CLI()
