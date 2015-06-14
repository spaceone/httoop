# -*- coding: utf-8 -*-
from httoop.codecs.multipart.multipart import Multipart

__all__ = ['MultipartMixed', 'MultipartFormData', 'MultipartAlternative', 'MultipartDigest', 'MultipartParallel']


class MultipartMixed(Multipart):

	mimetype = 'multipart/mixed'


class MultipartFormData(Multipart):

	mimetype = 'multipart/form-data'


class MultipartAlternative(Multipart):

	mimetype = 'multipart/alternative'


class MultipartDigest(Multipart):

	mimetype = 'multipart/digest'
	default_content_type = 'message/rfc822; charset=US-ASCII'


class MultipartParallel(Multipart):

	mimetype = 'multipart/parallel'
