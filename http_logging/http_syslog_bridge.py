"""Log POST requests to a syslog instance.

This module is kept simple for reliability: messages are forwarded
without modification.
"""

import time
import logging
import socket
import logging.handlers
import urllib.parse

class NopFormatter(logging.Formatter):
    def __init__(self, newline_terminate):
        self._newline_terminate = newline_terminate
        super(NopFormatter, self).__init__()

    def format(self, record):
        msg = record.msg
        return msg if not self._newline_terminate else msg + "\n"

def recover_record(s):
    qs_binary = urllib.parse.parse_qsl(s)
    qs = {k.decode("utf-8"): v.decode("utf-8") for k, v in qs_binary}
    record = logging.LogRecord(args=(), exc_info=None, **qs)
    return record

class Bridge:
    """The bridge is a WSGI application that expects a POST request.

    The body of the request must contain a urlencoded query string.

    The string must contain all parameters needed to construct a
    logging.LogRecord object with the exception of `args` and `exc_info`
    as these could contain arbitrary object which cannot be reliably
    serialized.

    Given that record will never have `args`, the msg field is sent as
    is.
    """

    def __init__(self, syslog_opts={}, max_post_size = 4*1024):
        self._syslog_handler = logging.handlers.SysLogHandler(
                            **syslog_opts)
        protocol_is_tcp = self._syslog_handler.socktype == socket.SOCK_STREAM
        self._syslog_handler.setFormatter(NopFormatter(protocol_is_tcp))

        self._max_post_size = max_post_size

    def __call__(self, environ, start_response):
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH',
                                    self._max_post_size))
        except ValueError:
            request_body_size = self._max_post_size

        limited_body_size = min(self._max_post_size, request_body_size)

        request_body = environ['wsgi.input'].read(limited_body_size)

        record = recover_record(request_body)
        self._syslog_handler.emit(record)

        status = '200 OK'

        response_body = "{}\n".format(time.time()).encode("utf-8")

        response_headers = [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(response_body)))
        ]

        start_response(status, response_headers)
        return [response_body]

def main():
    import argparse
    import wsgiref.simple_server

    SOCKTYPES = {'tcp': socket.SOCK_STREAM, 'udp': socket.SOCK_DGRAM}
    SOCKCHOICE = list(sorted(SOCKTYPES.values()))

    opt_parser = argparse.ArgumentParser(
                    description = "HTTP (POST) to syslog bridge)")
    opt_parser.add_argument("syslog_server", help = "syslog server address or hostname")
    opt_parser.add_argument("syslog_port", help = "syslog server port", type=int)
    opt_parser.add_argument("syslog_fac", help = "syslog facility",
                                nargs = '?', default = "local0")

    opt_parser.add_argument("--proto", help = "SysLog protocol",
                            default = 'tcp', choices=SOCKCHOICE)

    opt_parser.add_argument("--max-size", help = "Maximum allowed size for POST request data",
                                type=int, default = 4*1024)

    opt_parser.add_argument("--listen", help = "Listen on address",
                                default = "127.0.0.1")
    opt_parser.add_argument("--port", help = "Listen on port", type=int,
                                default = 8888)

    args = opt_parser.parse_args()

    syslog_opts = {'address': (args.syslog_server, args.syslog_port),
                   'facility': args.syslog_fac,
                   'socktype': SOCKTYPES[args.proto]}
    app = Bridge(syslog_opts=syslog_opts, max_post_size = args.max_size)

    httpd = wsgiref.simple_server.make_server (
        args.listen, # The host name
        args.port, # A port number where to wait for the request
        app # The application object
    )

    print("Running at http://{}:{}".format(args.listen, args.port))
    # Wait for a single request, serve it and quit
    httpd.serve_forever()

    print("Exiting\a")

if __name__ == "__main__":
    main()

