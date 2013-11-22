# -*- coding: utf-8 -*-
u"""Module containing various codecs which are
	common used in combination with HTTP
"""

__all__ = [
	'CODECS', 'Codec', 'Percent', 'QueryString', 'Enconv',
	'application', 'audio', 'example', 'image',
	'message', 'model', 'multipart', 'text', 'video'
]

import inspect

CODECS = dict()

import httoop.codecs.common
import httoop.codecs.application
import httoop.codecs.audio
import httoop.codecs.example
import httoop.codecs.image
import httoop.codecs.message
import httoop.codecs.model
import httoop.codecs.multipart
import httoop.codecs.text
import httoop.codecs.video

types = (application, audio, example, image, message, model, multipart, text, video)

from httoop.codecs.application import Percent, QueryString
from httoop.codecs.common import Codec

for _, member in (member for type_ in types for member in inspect.getmembers(type_, inspect.isclass)):
	if issubclass(member, Codec) and getattr(member, 'mimetype', None):
		CODECS[member.mimetype] = member
