import logging.handlers
import urllib.parse
import urllib.request
import ssl

class FormattedHTTPHandler(logging.Handler):
    """HTTP handler with a nicer constructor, that makes use of a
    formatter

    Only POST is supported. Only Basic authentication is supported.

    This formatter produces messages in the format expected by
    http_syslog_bridge.
    """

    def __init__(self, url, validate_certificate=True):
        """Parameters:
            url: of the HTTP/HTTPS endpoint. Logs will be sent as a POST
             request. url can be of the form http(s)://user:pass@host/q.
             The reques will then include de appropiate headers to
             perform authentication.
            validate_certificate: if False, SSL certificates will not be
             validated. Useful to test the system with "snakeoil"
             (i.e. self-signed) certificates.
        """
        self.url = urllib.parse.urlparse(url)
        user, _pass = self._username, self._password

        self._stripped_url = self._strip_user_pass()

        pw_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        pw_manager.add_password(realm=None,
                                uri=self._stripped_url,
                                user=user,
                                passwd=_pass)
        auth_handler = urllib.request.HTTPBasicAuthHandler(pw_manager)

        if not validate_certificate:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            handlers=[urllib.request.HTTPSHandler(context=ctx)]
        else:
            handlers=[]

        handlers.append(auth_handler)
        self._opener = urllib.request.build_opener(*handlers).open

        super().__init__()

    @property
    def _username(self):
        return self.url.username

    @property
    def _password(self):
        return self.url.password

    def _strip_user_pass(self):
        if self.url.port is not None:
            netloc = "{}:{}".format(self.url.hostname, self.url.port)
        else:
            netloc = self.url.hostname

        url_without_auth = urllib.parse.ParseResult(
                            scheme=self.url.scheme,
                            netloc=netloc,
                            path=self.url.path,
                            params=self.url.params,
                            query=self.url.query,
                            fragment=self.url.fragment).geturl()

        return url_without_auth

    def mapLogRecord(self, record):
        msg = self.format(record)

        d = dict(record.__dict__)

        d['msg'] = msg
        d['level'] = self.level
        del d['args']
        del d['exc_info']

        return d

    def emit(self, record):
        """
        Emit a record.
        Send the record to the Web server as a percent-encoded dictionary
        """
        try:
            mrecord = self.mapLogRecord(record)
            data = urllib.parse.urlencode(mrecord).encode('utf-8')
            _req = urllib.request.Request(self._stripped_url, data)
            with self._opener(_req) as req:
                req.read() # discard data
        except Exception:
            self.handleError(record)

def test():
    import argparse
    import logging

    opt_parser = argparse.ArgumentParser(
                    description = "POST a logging message to syslog bridge)")
    opt_parser.add_argument("url", help = "syslog server address or hostname")
    opt_parser.add_argument("message", help = "syslog facility")

    args = opt_parser.parse_args()

    handler = FormattedHTTPHandler(args.url)
    logging.getLogger().addHandler(handler)

    logging.warning(args.message)

if __name__ == "__main__":
    test()
