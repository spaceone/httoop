# -*- coding: utf-8 -*-
u"""Module containing various codecs which are
	common used in combination with HTTP
"""

__all__ = [
	'CODECS', 'Codec',
	'application', 'audio', 'example', 'image',
	'message', 'model', 'multipart', 'text', 'video'
]

import inspect

CODECS = dict()

from httoop.codecs import application
from httoop.codecs import audio
from httoop.codecs import example
from httoop.codecs import image
from httoop.codecs import message
from httoop.codecs import model
from httoop.codecs import multipart
from httoop.codecs import text
from httoop.codecs import video

types = (application, audio, example, image, message, model, multipart, text, video)

from httoop.codecs.codec import Codec


def lookup(encoding, raise_errors=True):
	type_ = '%s/*' % (encoding.split('/', 1)[0],)
	return CODECS.get(encoding) or CODECS.get(type_) or (raise_errors and CODECS[encoding]) or None


def register(encoding, codec):
	CODECS[encoding] = codec


for _, member in (member for type_ in types for member in inspect.getmembers(type_, inspect.isclass)):
	if issubclass(member, Codec) and getattr(member, 'mimetype', None):
		CODECS[member.mimetype] = member
