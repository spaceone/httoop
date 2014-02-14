httoop
======

An object oriented HTTP library.

Httoop can be used to parse, compose and work with HTTP-Request- and Response-Messages.

It is an generic library for implementing HTTP servers, clients, caches and proxies.

Httoop provides an powerful interface using the vocabularity used in RFC 2616 and focuses on implementing HTTP "compliant" as defined in RFC 2616 Section 1.2.

"An implementation is not compliant if it fails to satisfy one or more of the MUST or REQUIRED level requirements for the protocols it implements."
[RFC 2616 Section 1.2](http://tools.ietf.org/html/rfc2616#section-1.2)

On top of the object oriented abstraction of HTTP httoop provides an easy way to support WSGI.


HTTP and extensions are defined in the following RFC's:

* HTTP/1.1 [Message Syntax and Routing](http://tools.ietf.org/html/draft-ietf-httpbis-p1-messaging-26)

* HTTP/1.1 [Semantics and Content](http://tools.ietf.org/html/draft-ietf-httpbis-p2-semantics-26)

* HTTP/1.1 [Conditional Requests](http://tools.ietf.org/html/draft-ietf-httpbis-p4-conditional-26)

* HTTP/1.1 [Range Requests](http://tools.ietf.org/html/draft-ietf-httpbis-p5-range-26)

* HTTP/1.1 [Caching](http://tools.ietf.org/html/draft-ietf-httpbis-p6-cache-26)

* HTTP/1.1 [Authentication](http://tools.ietf.org/html/draft-ietf-httpbis-p7-auth-26)

* Hypertext Transfer Protocol -- HTTP/1.1 (RFC 2616)

* Internet Message Format (RFC 822, 2822, 5322)

* HTTP Authentication: Basic and Digest Access Authentication (RFC 2617)

* Additional HTTP Status Codes (RFC 6585)

* PATCH Method for HTTP (RFC 5789)

* Use of the Content-Disposition Header Field in the Hypertext Transfer Protocol (HTTP) (RFC 6266)

* Upgrading to TLS Within HTTP/1.1 (RFC 2817)

* Transparent Content Negotiation in HTTP (RFC 2295)

* HTTP Remote Variant Selection Algorithm -- RVSA/1.0 (RFC 2296)

* HTTP Extensions for Web Distributed Authoring and Versioning (WebDAV) (RFC 4918)

* Hyper Text Coffee Pot Control Protocol (HTCPCP/1.0) (RFC 2324)

Extended information about hypermedia, WWW and how HTTP is meant to be used:

* Web Linking (RFC 5988)

* Representational State Transfer [REST](http://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
