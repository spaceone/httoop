# -*- coding: utf-8 -*-
from httoop.codecs.multipart.multipart import Multipart

__all__ = ['MultipartMixed', 'MultipartMixedReplace', 'MultipartFormData', 'MultipartAlternative', 'MultipartDigest', 'MultipartParallel', 'MultipartByteranges']


class MultipartMixed(Multipart):

	mimetype = 'multipart/mixed'


class MultipartMixedReplace(Multipart):

	mimetype = 'multipart/x-mixed-replace'


class MultipartFormData(Multipart):

	mimetype = 'multipart/form-data'


class MultipartAlternative(Multipart):

	mimetype = 'multipart/alternative'


class MultipartDigest(Multipart):

	mimetype = 'multipart/digest'
	default_content_type = 'message/rfc822; charset=US-ASCII'


class MultipartParallel(Multipart):

	mimetype = 'multipart/parallel'


class MultipartByteranges(Multipart):

	mimetype = 'multipart/byteranges'
