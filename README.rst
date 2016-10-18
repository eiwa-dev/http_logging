===================
Better HTTP Logging
===================

---------------------------------------
http_handler: a better http log handler
---------------------------------------

The HTTP log handler that comes with Python's standard lib is too
complex for too few features. This one uses urllib.request for a simpler
and more capable implementation.

It also tries to format the log record a bit more intelligently.

Features
--------

* Supports HTTPS
* Supports Basic Authentication
* User and password are specified using user:pass@host.domain

---------------------
HTTP-to-Syslog bridge
---------------------

This module allows you to forward messages delivered over a HTTP POST
request to a remote syslog server.

Key Features
------------

* Messages are forwarded almost unmodified to syslog.
* No https or auth whatsoever. Handle that with a real proxy server.

Usage
-----

The server can be run standalone, using the wsgiref module or you can
write a small scrip to import the app into uWSGI or something of the sort.

Sample uWSGI/NGINX config
-------------------------

TODO!