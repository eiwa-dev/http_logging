
import argparse
import logging

from cee_formatter import CEEFormatter
from http_handler import FormattedHTTPHandler

opt_parser = argparse.ArgumentParser(
                description = "POST a logging message to syslog bridge)")
opt_parser.add_argument("url", help = "syslog server address or hostname")
opt_parser.add_argument("message", help = "syslog facility")

args = opt_parser.parse_args()

handler = FormattedHTTPHandler(args.url)
fmt = CEEFormatter()
handler.setFormatter(fmt)

logging.getLogger().addHandler(handler)

logging.warning(args.message)
