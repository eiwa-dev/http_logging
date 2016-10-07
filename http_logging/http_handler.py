import logging.handlers
import urllib.parse
import urllib.request

class FormattedHTTPHandler(logging.Handler):
    """HTTP handler with a nicer constructor, that makes use of a
    formatter

    Only POST is supported.

    This formatter produces messages in the format expected by
    http_syslog_bridge.
    """

    def __init__(self, url):
        self.url = url
        super().__init__()

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
            with urllib.request.urlopen(self.url, data) as req:
                print(req.read()) # discard data
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
