# -*- coding: utf-8 -*-

from hashlib import md5

from httoop.exceptions import InvalidHeader
from httoop.header.element import HeaderElement
from httoop.util import _


class DigestAuthScheme(object):

	algorithms = {
		'MD5': lambda val: md5(val).hexdigest(),
		'MD5-sess': lambda val: md5(val).hexdigest(),
	}
	qops = ('auth', 'auth-int')  # quality of protection

	@classmethod
	def get_algorithm(cls, algorithm):
		try:
			return cls.algorithms[algorithm]
		except KeyError:
			raise InvalidHeader(_(u'Unknown digest authentication algorithm: %r'), algorithm)

	@classmethod
	def compose(cls, authinfo):
		params = cls._compose(authinfo)
		return b', '.join([HeaderElement.formatparam(k, v) for k, v in params])

	@classmethod
	def _compose(cls, authinfo):  # pragma: no cover
		return authinfo

	@classmethod
	def parse(cls, authinfo):
		atoms = [x.strip() for x in authinfo.split(',') if x.strip()] or ['']

		params = dict((key.strip(), value.strip().strip('"')) for key, _, value in (atom.partition('=') for atom in atoms))
		return params


class DigestAuthResponseScheme(DigestAuthScheme):

	@classmethod
	def _compose(cls, authinfo):
		realm = authinfo['realm']
		algorithm = authinfo.get('algorithm', 'MD5')
		domain = authinfo.get('domain')
		if isinstance(domain, (list, tuple)):
			domain = ' '.join(domain)
		nonce = authinfo['nonce'].replace('"', '')

		stale = authinfo.get('stale')
		if isinstance(stale, bool):
			stale = 'true' if stale else 'false'

		qop_options = authinfo.get('qop', tuple(cls.qops))
		if isinstance(qop_options, (list, tuple)):
			qop_options = ','.join(qop_options)

		params = [
			('realm', realm),
			('domain', domain),
			('nonce', nonce),
			('opaque', authinfo.get('opaque')),
			('stale', stale),
			('algorithm', algorithm),
			('qop', qop_options),
			authinfo.get('auth-param', [None, None])
		]
		return [(k, v) for k, v in params if v is not None]

	@classmethod
	def parse(cls, authinfo):
		params = super(cls, cls).parse(authinfo)
		if '"' in params['nonce']:
			raise InvalidHeader(_(u'Nonce must not contain double quote'))
		stale = params.get('stale')
		if stale:
			stale = {'false': False, 'true': True}.get(stale.lower())
		params = [
			('realm', params['realm']),
			('domain', params.get('domain', '').split()),
			('nonce', params['nonce']),
			('opaque', params.get('opaque')),
			('stale', stale),
			('algorithm', params.get('algorithm')),
			('qop', [p.strip() for p in params.get('qop', '').split(',')]),
		]
		return dict([(k, v) for k, v in params if v is not None])


class DigestAuthRequestScheme(DigestAuthScheme):

	@classmethod
	def _compose(cls, authinfo):
		username = authinfo['username']
		realm = authinfo['realm']
		digest_uri = authinfo['uri']
		nonce = authinfo.get('nonce', '').replace('"', '')
		response = authinfo.get('response')
		cnonce = None
		nonce_count = None
		message_qop = authinfo.get('qop')
		if message_qop:
			cnonce = authinfo['cnonce']
			nonce_count = authinfo['nc']

		params = [
			('username', username),
			('realm', realm),
			('nonce', nonce or cls.generate_nonce(authinfo)),
			('uri', digest_uri),
			('response', response or cls.calculate_request_digest(authinfo)),
			('algorithm', authinfo.get('algorithm')),
			('cnonce', cnonce),
			('opaque', authinfo.get('opaque')),
			('qop', message_qop),
			('nc', nonce_count),
			authinfo.get('auth-param', [None, None])
		]
		return [(k, v) for k, v in params if v is not None]

	@classmethod
	def parse(cls, authinfo):
		params = super(cls, cls).parse(authinfo)
		message_qop = params.get('qop')
		cnonce = None
		nonce_count = None
		if message_qop:
			cnonce = params['cnonce']
			nonce_count = params['nc']
		params = [
			('username', params['username']),
			('realm', params['realm']),
			('nonce', params['nonce']),
			('uri', params['uri']),
			('response', params['response']),
			('algorithm', params.get('algorithm')),
			('cnonce', cnonce),
			('opaque', params.get('opaque')),
			('qop', message_qop),
			('nc', nonce_count),
		]
		return dict([(k, v) for k, v in params if v is not None])

	@classmethod
	def generate_nonce(cls, authinfo):
		from time import time
		from uuid import uuid4
		nonce = '%d:%s:%s' % (time(), authinfo.get('etag', authinfo.get('realm')), uuid4(), )
		algorithm = authinfo.get('algorithm', 'MD5')
		H = cls.get_algorithm(algorithm)
		return H(nonce)

	@classmethod
	def check(cls, authinfo, request_params):
		if authinfo['realm'] != request_params['realm']:
			return False
		response = cls.calculate_request_digest(authinfo)
		return response == request_params['response']

	@classmethod
	def calculate_request_digest(cls, authinfo):
		algorithm = authinfo.get('algorithm', 'MD5')
		H = cls.get_algorithm(algorithm)

		if algorithm == 'MD5-sess' and authinfo.get('A1'):
			secret = H(authinfo['A1'])
		else:
			secret = H(cls.A1(authinfo))

		qop = authinfo.get('qop')
		hash_a2 = H(cls.A2(authinfo))
		if qop in ('auth', 'auth-int'):
			data = b'%s:%s:%s:%s:%s' % (authinfo['nonce'], authinfo['nc'], authinfo['cnonce'], authinfo['qop'], hash_a2)
		elif qop is None:
			data = b'%s:%s' % (authinfo['nonce'], hash_a2)
		else:
			raise NotImplementedError('Unknown quality of protection: %r' % (qop,))

		return H(b'%s:%s' % (secret, data))

	@classmethod
	def A2(cls, params):
		qop = params.get('qop', '')
		if not qop or qop == 'auth':
			return b'%s:%s' % (params['method'], params['uri'])
		elif qop == 'auth-int':
			H = cls.get_algorithm(params['algorithm'])
			return b'%s:%s:%s' % (params['method'], params['uri'], H(params['entity_body']))
		else:
			raise NotImplementedError('Unknown quality of protection: %r' % (qop,))

	@classmethod
	def A1(cls, params):
		algorithm = params.get('algorithm', '')

		if not algorithm or algorithm == 'MD5':
			return b'%s:%s:%s' % (params['username'], params['realm'], params['password'])
		elif algorithm == 'MD5-sess':
			H = cls.get_algorithm(algorithm)
			s = b'%s:%s:%s' % (params['username'], params['realm'], params['password'])
			return b'%s:%s:%s' % (H(s), params['nonce'], params['cnonce'])
		else:
			raise NotImplementedError('Unknown algorithm: %s' % (algorithm,))
