# -*- coding: utf-8 -*-
"""JSON Hypertext Application Language (application/hal+json) codec"""

from __future__ import absolute_import

try:
	from uritemplate import expand
except ImportError:
	# TODO: emit a warning
	def expand(href, **templates):
		for templ, value in templates.items():
			href = href.replace('{%s}' % (templ,), value)
		return href

from httoop.codecs.application.json import JSON
from httoop.exceptions import DecodeError, EncodeError
from httoop.six import string_types


class Resource(dict):
	"""A JSON Hypertext Application Language resource"""

	def __init__(self, *args, **kwargs):
		super(Resource, self).__init__(*args, **kwargs)
		self.setdefault('_links', {})
		self.setdefault('_embedded', {})
		if not isinstance(self['_links'], dict):
			raise DecodeError(u'HAL links must be JSON objects.')
		if not isinstance(self['_embedded'], dict):
			raise DecodeError(u'HAL embedded must be JSON objects.')

	@property
	def self(self):
		return self.expand(self.get_link('self')['href'])

	def get_links(self, relation, name=None):
		links = self['_links'].get(relation)
		if links is None:
			return
		if isinstance(links, dict):
			links = [links]
		if not isinstance(links, (list, tuple)):
			raise DecodeError(u'HAL links must be arrays or objects')
		for link in links:
			if not isinstance(link, dict):
				raise DecodeError(u'HAL link must be object')
			if not isinstance(link.get('href'), string_types):
				raise DecodeError(u'HAL links must contain href')
			if name is not None and link.get('name') != name:
				continue
			link.setdefault('templated', False)
			link.setdefault('deprecation', False)
			link.setdefault('name', None)
			link.setdefault('type', None)
			link.setdefault('profile', None)
			link.setdefault('hreflang', None)
			for key in ('name', 'type', 'profile', 'hreflang'):
				if not isinstance(link[key], string_types):
					link[key] = None
			if not isinstance(link['templated'], bool):
				link['templated'] = False
			if not isinstance(link['deprecation'], bool):
				link['deprecation'] = False
			yield link

	def get_link(self, relation, name=None):
		try:
			return next(self.get_links(relation, name))
		except StopIteration:
			pass

	def get_relations(self):
		return list(set(self['_links'].keys()) | set(self['_embedded'].keys()))

	def get_resources(self, relation):
		embedded = self['_embedded'].get(relation)
		if not embedded:
			return
		if isinstance(embedded, dict):
			embedded = [embedded]
		for resource in embedded:
			if not isinstance(resource, dict):
				raise DecodeError(u'HAL resources must be objects')
			yield Resource(resource.copy())

	def get_resource(self, relation):
		try:
			return next(self.get_resources(relation))
		except StopIteration:
			pass

	def expand(___self, ___href, **templates):
		return expand(___href, **templates)

	def get_curie(self, relation):
		if ':' in relation:
			name, rel = relation.split(':', 1)
			link = self.get_link('curie', name)
			if link:
				return self.expand(link['href'], rel=rel)
		return relation

	def add_link(self, relation, link):
		links = self['_links'].setdefault(relation, [])
		if not isinstance(links, list):
			links = [links]
		links.append(link)
		self['_links'][relation] = links
		self['_links'][relation] = list(self.get_links(relation))

	def add_resource(self, relation, resource):
		resources = list(self.get_resources(relation))
		resources.append(resource)
		self['_embedded'][relation] = resources


class HAL(JSON):
	mimetype = 'application/hal+json'

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):
		data = super(HAL, cls).decode(data)
		if not isinstance(data, dict):
			raise DecodeError(u'HAL documents must be JSON objects.')
		return Resource(data)

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):
		if not isinstance(data, dict):
			raise EncodeError(u'HAL documents must be JSON objects.')

		try:
			Resource(data.copy())
		except DecodeError as exc:
			raise EncodeError(str(exc))

		return super(HAL, cls).encode(data)
