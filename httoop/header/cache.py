from httoop.header.element import HeaderElement


class Age(HeaderElement):

    is_response_header = True


class CacheControl(HeaderElement, name='Cache-Control'):

    is_request_header = True
    is_response_header = True


class Expires(HeaderElement):

    is_response_header = True


class Pragma(HeaderElement):

    is_response_header = True


class Vary(HeaderElement):

    is_response_header = True


class Warning(HeaderElement):  # noqa: A001

    is_response_header = True
