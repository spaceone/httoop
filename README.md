[![Build Status](https://travis-ci.org/spaceone/httoop.svg)](https://travis-ci.org/spaceone/httoop)
[![codecov](https://codecov.io/gh/spaceone/httoop/branch/master/graph/badge.svg)](https://codecov.io/gh/spaceone/httoop)
[![Code Climate](https://codeclimate.com/github/spaceone/httoop/badges/gpa.svg)](https://codeclimate.com/github/spaceone/httoop)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/spaceone/httoop/raw/master/LICENSE)

httoop
======

An object oriented HTTP/1.1 library. (HTTP/2 will probably follow in the future).

Httoop can be used to parse, compose and work with HTTP-Request- and Response-Messages.

It is an generic library for implementing HTTP servers, clients, caches and proxies.

Httoop provides an powerful interface using the vocabularity used in RFC 7230 - 7235 and focuses on implementing HTTP "compliant" as defined in [RFC 7230 Section 2.5](https://datatracker.ietf.org/doc/html/rfc7230#section-2.5).

"An implementation is not compliant if it fails to satisfy one or more of the MUST or REQUIRED level requirements for the protocols it implements."
[RFC 2616 Section 1.2](https://datatracker.ietf.org/doc/html/rfc2616#section-1.2)

On top of the object oriented abstraction of HTTP httoop provides an easy way to support WSGI.


HTTP and extensions are defined in the following RFC's:

* HTTP/1.1 RFC 7230 [Message Syntax and Routing](https://datatracker.ietf.org/doc/html/rfc7230)

* HTTP/1.1 RFC 7231 [Semantics and Content](https://datatracker.ietf.org/doc/html/rfc7231)

* HTTP/1.1 RFC 7232 [Conditional Requests](https://datatracker.ietf.org/doc/html/rfc7232)

* HTTP/1.1 RFC 7233 [Range Requests](https://datatracker.ietf.org/doc/html/rfc7233)

* HTTP/1.1 RFC 7234 [Caching](https://datatracker.ietf.org/doc/html/rfc7234)

* HTTP/1.1 RFC 7235 [Authentication](https://datatracker.ietf.org/doc/html/rfc7235)

* <s>Hypertext Transfer Protocol -- HTTP/1.1 ([RFC 2616](https://datatracker.ietf.org/doc/html/rfc2616)) </s>

* HTTP/2 RFC 7540 [Hypertext Transfer Protocol Version 2](https://datatracker.ietf.org/doc/html/rfc7540)

* HTTP/2 RFC 7541 [HPACK: Header Compression for HTTP/2](https://datatracker.ietf.org/doc/html/rfc7541)

* [IANA HTTP Status Codes](http://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml)

* [IANA HTTP Methods](http://www.iana.org/assignments/http-methods/http-methods.xhtml)

* [IANA Message Headers](http://www.iana.org/assignments/message-headers/message-headers.xhtml)

* [IANA URI Schemes](http://www.iana.org/assignments/uri-schemes/uri-schemes.xhtml)

* [IANA HTTP Authentication Schemes](http://www.iana.org/assignments/http-authschemes/http-authschemes.xhtml)

* [IANA HTTP Cache Directives](http://www.iana.org/assignments/http-cache-directives/http-cache-directives.xhtml)

* RFC 5987 [Character Set and Language Encoding for Hypertext Transfer Protocol (HTTP) Header Field Parameters](https://datatracker.ietf.org/doc/html/rfc5987)

* Uniform Resource Identifier (URI) ([RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986))

* Internet Message Format ([RFC 822](https://datatracker.ietf.org/doc/html/rfc822), [2822](https://datatracker.ietf.org/doc/html/rfc2822), [5322](https://datatracker.ietf.org/doc/html/rfc5322))

* <s>HTTP Authentication: Basic and Digest Access Authentication ([RFC 2617](https://datatracker.ietf.org/doc/html/rfc2617))</s>

* HTTP Authentication-Info and Proxy-Authentication-Info Response Header Fields ([RFC 7615](https://datatracker.ietf.org/doc/html/rfc7615))

* HTTP Digest Access Authentication ([RFC 7616](https://datatracker.ietf.org/doc/html/rfc7616))

* The 'Basic' HTTP Authentication Scheme ([RFC 7617](https://datatracker.ietf.org/doc/html/rfc7617))

* Additional HTTP Status Codes ([RFC 6585](https://datatracker.ietf.org/doc/html/rfc6585))

* Forwarded HTTP Extension [RFC 7239](https://datatracker.ietf.org/doc/html/rfc7239)

* Prefer Header for HTTP [RFC 7240](https://datatracker.ietf.org/doc/html/rfc7240)

* PATCH Method for HTTP ([RFC 5789](https://datatracker.ietf.org/doc/html/rfc5789))

* JavaScript Object Notation (JSON) Patch ([RFC 6902](https://datatracker.ietf.org/doc/html/rfc6902))

* Use of the Content-Disposition Header Field in the Hypertext Transfer Protocol (HTTP) ([RFC 6266](https://datatracker.ietf.org/doc/html/rfc6266))

* Upgrading to TLS Within HTTP/1.1 ([RFC 2817](https://datatracker.ietf.org/doc/html/rfc2817))

* Transparent Content Negotiation in HTTP ([RFC 2295](https://datatracker.ietf.org/doc/html/rfc2295))

* HTTP Remote Variant Selection Algorithm -- RVSA/1.0 ([RFC 2296](https://datatracker.ietf.org/doc/html/rfc2296))

* HTTP State Management Mechanism ([RFC 6265](https://datatracker.ietf.org/doc/html/rfc6265))

* Same-site Cookies ([Draft 7](https://datatracker.ietf.org/doc/html/rfcdraft-west-first-party-cookies-07))

* HTTP Extensions for Web Distributed Authoring and Versioning (WebDAV) ([RFC 4918](https://datatracker.ietf.org/doc/html/rfc4918))

* Hyper Text Coffee Pot Control Protocol (HTCPCP/1.0) ([RFC 2324](https://datatracker.ietf.org/doc/html/rfc2324))

Extended information about hypermedia, WWW and how HTTP is meant to be used:

* Web Linking ([RFC 5988](https://datatracker.ietf.org/doc/html/rfc5988))

* Representational State Transfer [REST](http://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)

  * [REST APIs must be hypertext-driven](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven)

  * [Specialization](https://roy.gbiv.com/untangled/2008/specialization)

  * [No REST in CMIS](https://roy.gbiv.com/untangled/2008/no-rest-in-cmis)

  * [On software architecture](https://roy.gbiv.com/untangled/2008/on-software-architecture)

  * [It is okay to use POST](https://roy.gbiv.com/untangled/2009/it-is-okay-to-use-post)

  * [Paper tigers and hidden dragons](https://roy.gbiv.com/untangled/2008/paper-tigers-and-hidden-dragons)

  * [Economies of scale](https://roy.gbiv.com/untangled/2008/economies-of-scale)

* [Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)

* [Test Cases for HTTP Content-Disposition header field](http://greenbytes.de/tech/tc2231/)

* [Cross-Origin Resource Sharing](http://www.w3.org/TR/cors/)

* [HTTP (HTML) Leaks](https://github.com/cure53/HTTPLeaks/blob/main/leak.html)

OAuth 2.0:

* [OAuth Working Group Specifications](https://oauth.net/specs/)
* [OAuth 2.0 Security Best Current Practice](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
* [The OAuth 2.0 Authorization Framework](https://datatracker.ietf.org/doc/html/rfc6749)
* [Bearer Token Usage](https://datatracker.ietf.org/doc/html/rfc6750)
* [JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)
* [JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens](https://datatracker.ietf.org/doc/html/rfc9068)
* [Resource Indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707)
