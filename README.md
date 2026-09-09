[![Build Status](https://github.com/spaceone/httoop/actions/workflows/ci.yml/badge.svg)](https://github.com/spaceone/httoop/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/spaceone/httoop/branch/master/graph/badge.svg)](https://codecov.io/gh/spaceone/httoop)
[![Code Climate](https://codeclimate.com/github/spaceone/httoop/badges/gpa.svg)](https://codeclimate.com/github/spaceone/httoop)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/spaceone/httoop/raw/master/LICENSE)

httoop
======

An object-oriented HTTP/1.x protocol library for Python.

Httoop is for applications that need to understand HTTP, not merely send a request.
It parses and composes requests and responses, and gives every important part of a message a useful object: methods, URIs, protocols, headers, statuses, and bodies.
The same model can be used to build protocol-aware clients, servers, gateways, middleware, caches, and proxies.

## Why httoop?

Most HTTP libraries make the network convenient by hiding the protocol.
Httoop takes a different approach: it makes the protocol convenient to work with.
You can inspect, validate, transform, and re-compose a message without dropping down to ad-hoc string manipulation or abandoning the HTTP wire format.

* **One coherent object model.** HTTP values share a small semantic interface: they can be parsed, composed, converted to bytes, compared, and represented consistently.
* **Incremental by design.** The state-machine parser accepts fragmented input, supports pipelined messages, handles fixed-length and chunked bodies, and preserves trailers.
* **Structured instead of stringly typed.** Headers and URIs expose parsed components, parameters, normalization, joining, and validation. Cookies, ranges, content types, dates, authentication fields, and security headers do not need to be hand-parsed.
* **Streaming without special cases.** A body can be bytes, text, a file, a file-like object, or an iterable. The same body abstraction handles content encoding, transfer encoding, chunking, and limits.
* **Protocol-aware composition.** Request and response preparation takes care of HTTP details such as `Host`, `Content-Length`, `Date`, connection semantics, bodyless statuses, `HEAD`, and byte ranges.
* **Safe boundaries for untrusted input.** Header counts and sizes, URI lengths, body sizes, and decompressed body sizes can be bounded explicitly, while malformed framing and invalid fields are rejected.
* **Designed to be extended.** New header elements, URI schemes, statuses, and media codecs can be registered and used through the same interfaces as the built-ins.
* **Integration where it matters.** WSGI support provides a bridge to existing Python web applications without requiring a second message representation.

## The Zen of httoop

Httoop follows a few simple principles:

1. **Model HTTP as meaning, not as text.** Wire bytes are an input and output format; inside the application, HTTP should be represented by objects with explicit semantics.
2. **Separate syntax, semantics, and transport.** Parsing answers "is this a valid message?", composition answers "what should this message mean on the wire?", and adapters answer "where does it run?". Each layer can evolve independently.
3. **Make the wire visible when it matters.** Httoop does not hide framing, headers, status codes, encodings, or protocol versions. This makes unusual HTTP behavior possible to inspect and reason about.
4. **Treat partial input and large bodies as normal.** Streaming, buffering, pipelining, and resource limits are part of the model rather than afterthoughts.
5. **Prefer composition over special-purpose APIs.** The same `Request`, `Response`, `Headers`, `URI`, and `Body` objects work across clients, servers, gateways, and middleware.
6. **Extend by adding knowledge, not by rewriting the core.** Protocol extensions plug into registries and semantic types instead of requiring changes throughout the parser.

## HTTP standards

HTTP and extensions are defined in the following RFC's:

* [RFC 9110 HTTP Semantics](https://datatracker.ietf.org/doc/html/rfc9110)

* HTTP/1.1 RFC 7234 [Caching](https://datatracker.ietf.org/doc/html/rfc7234)

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

* HTTP Digest Access Authentication ([RFC 7616](https://datatracker.ietf.org/doc/html/rfc7616))

* The 'Basic' HTTP Authentication Scheme ([RFC 7617](https://datatracker.ietf.org/doc/html/rfc7617))

* Additional HTTP Status Codes ([RFC 6585](https://datatracker.ietf.org/doc/html/rfc6585))

* Forwarded HTTP Extension [RFC 7239](https://datatracker.ietf.org/doc/html/rfc7239)

* Prefer Header for HTTP [RFC 7240](https://datatracker.ietf.org/doc/html/rfc7240)

* PATCH Method for HTTP ([RFC 5789](https://datatracker.ietf.org/doc/html/rfc5789))

* JavaScript Object Notation (JSON) Patch ([RFC 6902](https://datatracker.ietf.org/doc/html/rfc6902))

* The HTTP QUERY Method ([RFC 10008](https://datatracker.ietf.org/doc/html/rfc10008))

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

* Clarifications of misconceptions people have about REST:

 * [Do You Really Understand the REST?](https://t-code.pl/blog/2016/02/rest-misconceptions-0/)

 * [the URI Confusion](https://t-code.pl/blog/2016/02/rest-misconceptions-1/)

 * [(Not) Linking Data (Enough)](https://t-code.pl/blog/2016/02/rest-misconceptions-2/)

 * [More Than Links](https://t-code.pl/blog/2016/03/rest-misconceptions-3/)

 * [Resources Are Application State](https://t-code.pl/blog/2016/03/rest-misconceptions-4/)

 * [REST "Documentation"](https://t-code.pl/blog/2016/03/rest-misconceptions-5/)

 * [Versioning and Hypermedia](https://t-code.pl/blog/2016/03/rest-misconceptions-6/)

 * [HATEOAS as if You Meant It](https://t-code.pl/blog/2015/01/hateoas-as-if-you-meant-it/)

 * [The Labours of Hypermedia](https://t-code.pl/blog/2016/04/labours-of-hypermedia/)

 * [Hypermedia must be extensible - Extensible Media Types](https://t-code.pl/blog/2016/04/hypermedia-must-be-extensible/)

 * [Consuming Hypermedia - Declarative UI](https://t-code.pl/blog/2016/04/hypermedia-driven-ui/)

 * [Towards Server-side Routing With URI Templates (RFC 6570)](https://t-code.pl/blog/2016/11/towards-server-side-routing-with-uri-templates/)

 * [Testing APIs Hypermedia-style](https://t-code.pl/blog/2019/06/testing-hypermedia-api/)

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

Obsolete:

* <s>HTTP/1.1 RFC 7230 [Message Syntax and Routing](https://datatracker.ietf.org/doc/html/rfc7230)</s>
* <s>HTTP/1.1 RFC 7231 [Semantics and Content](https://datatracker.ietf.org/doc/html/rfc7231)</s>
* <s>HTTP/1.1 RFC 7232 [Conditional Requests](https://datatracker.ietf.org/doc/html/rfc7232)</s>
* <s>HTTP/1.1 RFC 7233 [Range Requests](https://datatracker.ietf.org/doc/html/rfc7233)</s>
* <s>HTTP/1.1 RFC 7235 [Authentication](https://datatracker.ietf.org/doc/html/rfc7235)</s>
* <s>Hypertext Transfer Protocol -- HTTP/1.1 ([RFC 2616](https://datatracker.ietf.org/doc/html/rfc2616)) </s>
* <s>HTTP Authentication: Basic and Digest Access Authentication ([RFC 2617](https://datatracker.ietf.org/doc/html/rfc2617))</s>
* <s>HTTP Authentication-Info and Proxy-Authentication-Info Response Header Fields ([RFC 7615](https://datatracker.ietf.org/doc/html/rfc7615))</s>
