"""
Module containing various codecs which are
common used in combination with HTTP.
"""

from __future__ import annotations

import inspect
from typing import Any

from httoop.codecs import application, audio, example, image, message, model, multipart, text, video
from httoop.codecs.codec import Codec


CODECS = {}
types = (application, audio, example, image, message, model, multipart, text, video)

__all__ = ['CODECS', 'Codec', 'application', 'audio', 'example', 'image', 'message', 'model', 'multipart', 'text', 'video']


def lookup(encoding: str, raise_errors: bool = True) -> Any:  # noqa: FBT001, FBT002
    type_ = '%s/*' % (encoding.split('/', 1)[0],)
    return CODECS.get(encoding) or CODECS.get(type_) or (raise_errors and CODECS[encoding]) or None


def register(encoding: str, codec: type[Codec]) -> None:
    CODECS[encoding] = codec


for _, member in (member for type_ in types for member in inspect.getmembers(type_, inspect.isclass)):
    if issubclass(member, Codec) and getattr(member, 'mimetype', None):
        CODECS[member.mimetype] = member
